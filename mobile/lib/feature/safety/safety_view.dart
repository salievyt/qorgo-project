import '../../core/design/qorgo_brand.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import '../../core/widgets/bottom_nav_bar.dart';
import '../../core/design/qorgo_theme.dart';
import 'package:flutter/material.dart';
import '../../domain/entities.dart';
import '../../domain/use_cases.dart';
import '../../core/widgets/sos_slider.dart';
import '../app/app_view_model.dart';
import 'forms.dart';
import '../maps/map_view.dart';

String timeLabel(DateTime value) {
  final v = value.toLocal();
  return '${v.day.toString().padLeft(2, '0')}.${v.month.toString().padLeft(2, '0')} ${v.hour.toString().padLeft(2, '0')}:${v.minute.toString().padLeft(2, '0')}';
}

class SafetyView extends StatefulWidget {
  const SafetyView({super.key, required this.controller, this.sosShortcut});
  final AppViewModel controller;
  final ValueListenable<int>? sosShortcut;
  @override
  State<SafetyView> createState() => _SafetyViewState();
}

class _SafetyViewState extends State<SafetyView> with WidgetsBindingObserver {
  static const _sosChannel = MethodChannel('qorgo/sos');
  int _tab = 0;
  bool _protectionExplained = false;
  AppViewModel get c => widget.controller;
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    widget.sosShortcut?.addListener(_openSosShortcut);
    WidgetsBinding.instance.addPostFrameCallback((_) => _explainProtection());
  }

  void _openSosShortcut() {
    if (!mounted) return;
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      if (!mounted || c.busy) return;
      final send = await showDialog<bool>(
          context: context,
          builder: (context) => AlertDialog(
                title: const Text('Отправить SOS?'),
                content: const Text(
                    'QORGO передаст вашим близким вашу последнюю доступную геопозицию.'),
                actions: [
                  TextButton(
                      onPressed: () => Navigator.pop(context, false),
                      child: const Text('Отмена')),
                  FilledButton(
                      onPressed: () => Navigator.pop(context, true),
                      child: const Text('Отправить SOS'))
                ],
              ));
      if (send == true) await c.activateSos();
    });
  }

  Future<void> _addSosShortcut() async {
    if (defaultTargetPlatform != TargetPlatform.android) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text(
              'На iPhone добавьте QORGO SOS через настройку экрана блокировки.')));
      return;
    }

    try {
      final state = await _sosChannel.invokeMethod<String>('requestAddTile');
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text(state == 'added'
              ? 'QORGO SOS добавлена в быстрые настройки.'
              : 'Подтвердите добавление QORGO SOS в системном диалоге или добавьте её через редактирование быстрых настроек.')));
    } on PlatformException {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text(
              'Не удалось открыть системное добавление. Добавьте QORGO SOS в быстрые настройки телефона.')));
    }
  }

  Future<void> _explainProtection() async {
    if (!mounted || _protectionExplained || !c.continuousProtection) return;
    if (!await c.shouldExplainProtection() || !mounted) return;
    _protectionExplained = true;
    final enabled = await showDialog<bool>(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
              title: const Text('Непрерывная защита'),
              content: const Text(
                  'QORGO будет передавать местоположение для безопасности: примерно раз в 30–60 секунд в движении и раз в 5–15 минут без движения. Во время SOS — чаще. Данные доступны доверенным близким и оператору только при активной тревоге, а история хранится 30 дней.'),
              actions: [
                TextButton(
                    onPressed: () => Navigator.pop(context, false),
                    child: const Text('Не сейчас')),
                FilledButton(
                    onPressed: () => Navigator.pop(context, true),
                    child: const Text('Разрешить и включить')),
              ],
            ));
    await c.markProtectionExplained();
    if (enabled == true) await c.startContinuousProtection();
    if (enabled == false) await c.setContinuousProtection(false);
  }

  @override
  void dispose() {
    widget.sosShortcut?.removeListener(_openSosShortcut);
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) c.refresh();
  }

  Widget _card(Widget child) => Card(
      elevation: 0,
      color: QorgoDesign.soft,
      child: Padding(padding: const EdgeInsets.all(20), child: child));
  Widget _heading(String text) => Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Text(text,
          style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w600)));
  void _showMap(GeoPoint point, String title) {
    Navigator.of(context).push(MaterialPageRoute<void>(
        builder: (_) => OpenStreetMapView(point: point, title: title)));
  }

  Widget _home(Snapshot data) {
    final alert = c.activeAlert;
    final hasContacts = data.contacts.isNotEmpty;
    final point = c.location;
    return Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
      Text(
          data.profile.name.isEmpty
              ? 'Ваш круг безопасности'
              : 'Здравствуйте, ${data.profile.name}',
          style: const TextStyle(
              fontSize: 14, color: QorgoDesign.muted, height: 1.4)),
      const SizedBox(height: 24),
      ..._incoming(data),
      if (alert != null)
        _alertCard(alert, expanded: true)
      else
        Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
              color: QorgoDesign.soft,
              borderRadius: BorderRadius.circular(24),
              border: Border.all(
                  color: hasContacts
                      ? QorgoDesign.danger.withValues(alpha: .22)
                      : QorgoDesign.border)),
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
            const Text('ЭКСТРЕННАЯ ПОМОЩЬ',
                style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w500,
                    letterSpacing: 1.4,
                    color: QorgoDesign.muted)),
            const SizedBox(height: 12),
            const Text('Нужна помощь?',
                style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.w600,
                    height: 1.15,
                    letterSpacing: -.7)),
            const SizedBox(height: 10),
            Text(
                hasContacts
                    ? 'Создайте SOS для своих близких.'
                    : 'Для SOS нужен хотя бы один близкий.',
                style: const TextStyle(
                    fontSize: 14, height: 1.5, color: QorgoDesign.muted)),
            const SizedBox(height: 24),
            if (hasContacts) ...[
              SosSlider(enabled: !c.busy, onActivate: c.activateSos),
              const SizedBox(height: 12),
              const Text('Потяните вправо до конца',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 12, color: QorgoDesign.muted)),
            ] else
              FilledButton.icon(
                  onPressed: c.busy ? null : () => editContact(context, c),
                  icon: const Icon(Icons.person_add_outlined, size: 20),
                  label: const Text('Добавить близкого')),
          ]),
        ),
      const SizedBox(height: 32),
      const Text('ВАШ ОБЗОР',
          style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w500,
              letterSpacing: 1.4,
              color: QorgoDesign.muted)),
      const SizedBox(height: 12),
      Card(
          child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 6),
              child: Column(children: [
                ListTile(
                    contentPadding:
                        const EdgeInsets.symmetric(horizontal: 20, vertical: 4),
                    leading: const Icon(Icons.people_outline,
                        size: 22, color: QorgoDesign.muted),
                    title: const Text('Круг безопасности',
                        style: TextStyle(
                            fontSize: 15, fontWeight: FontWeight.w500)),
                    subtitle: Text(
                        hasContacts
                            ? 'Близких: ${data.contacts.length}'
                            : 'Пока никого',
                        style: const TextStyle(
                            fontSize: 12, color: QorgoDesign.muted)),
                    trailing: const Icon(Icons.chevron_right,
                        size: 20, color: QorgoDesign.muted),
                    onTap: () => setState(() => _tab = 1)),
                const Divider(height: 1, indent: 62, endIndent: 20),
                ListTile(
                    contentPadding:
                        const EdgeInsets.symmetric(horizontal: 20, vertical: 4),
                    leading: const Icon(Icons.location_on_outlined,
                        size: 22, color: QorgoDesign.muted),
                    title: const Text('Местоположение',
                        style: TextStyle(
                            fontSize: 15, fontWeight: FontWeight.w500)),
                    subtitle: Text(
                        point == null
                            ? 'Не определено'
                            : 'Точность ±${point.accuracy.round()} м',
                        style: const TextStyle(
                            fontSize: 12, color: QorgoDesign.muted)),
                    trailing: IconButton(
                        tooltip: point == null
                            ? 'Определить местоположение'
                            : 'Открыть карту',
                        onPressed: c.busy
                            ? null
                            : () {
                                if (point == null) {
                                  c.updateLocation();
                                } else {
                                  _showMap(point, 'Моё местоположение');
                                }
                              },
                        icon: Icon(
                            point == null
                                ? Icons.my_location
                                : Icons.map_outlined,
                            size: 20,
                            color: QorgoDesign.accent)),
                    onTap: c.busy
                        ? null
                        : () {
                            if (point == null) {
                              c.updateLocation();
                            } else {
                              _showMap(point, 'Моё местоположение');
                            }
                          }),
              ]))),
    ]);
  }

  Widget _alertCard(SafetyAlert alert, {bool expanded = false}) =>
      _card(Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        Text(alert.title,
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 20)),
        Text(timeLabel(alert.createdAt)),
        const SizedBox(height: 8),
        Text(alert.status, style: const TextStyle(fontWeight: FontWeight.bold)),
        if (expanded) ...[
          const SizedBox(height: 8),
          for (final d in alert.deliveries) Text('${d.name}: ${d.label}'),
          const SizedBox(height: 8),
          const Text(
              'Принятие сервисом не подтверждает получение сообщения человеком.',
              style: TextStyle(fontSize: 12, color: QorgoDesign.muted)),
          if (alert.location == null) const Text('SOS создан без геопозиции.'),
          if (alert.location != null)
            TextButton.icon(
              onPressed: () => _showMap(alert.location!, 'Место SOS'),
              icon: const Icon(Icons.map_outlined),
              label: const Text('Место SOS'),
            ),
          if (alert.resolvedAt == null) ...[
            if (alert.deliveries.any((d) => d.status == 'unknown'))
              TextButton(
                  onPressed: c.busy
                      ? null
                      : () async {
                          final retry = await showDialog<bool>(
                              context: context,
                              builder: (ctx) => AlertDialog(
                                      title: const Text('Повторить отправку?'),
                                      content: const Text(
                                          'Результат предыдущей попытки неизвестен. Контакт может получить повторное сообщение.'),
                                      actions: [
                                        TextButton(
                                            onPressed: () =>
                                                Navigator.pop(ctx, false),
                                            child: const Text('Отмена')),
                                        FilledButton(
                                            onPressed: () =>
                                                Navigator.pop(ctx, true),
                                            child: const Text('Повторить'))
                                      ]));
                          if (retry == true) c.retryAlert(alert.id);
                        },
                  child: const Text('Повторить отправку')),
            OutlinedButton(
                onPressed: c.busy ? null : () => c.resolveAlert(alert.id),
                child: const Text('Я в безопасности')),
          ],
        ],
      ]));
  Widget _contacts(Snapshot data) =>
      Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        _heading('Мой круг безопасности'),
        Text('${data.contacts.length} из 20 контактов'),
        const SizedBox(height: 12),
        FilledButton.icon(
            onPressed: c.busy || data.contacts.length >= 20
                ? null
                : () => editContact(context, c),
            icon: const Icon(Icons.person_add_outlined),
            label: const Text('Добавить близкого')),
        const SizedBox(height: 16),
        if (data.contacts.isEmpty)
          _card(const Text(
              'Добавьте человека, которому доверяете. Его номер будет использоваться для SOS и быстрого звонка.')),
        for (final contact in data.contacts)
          _card(Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(contact.name,
                style:
                    const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            Text(contact.phone),
            if (contact.inQorgo)
              const Text('В QORGO',
                  style: TextStyle(color: QorgoDesign.accent, fontSize: 12)),
            if (contact.email.isNotEmpty) Text(contact.email),
            if (contact.relationship.isNotEmpty) Text(contact.relationship),
            Wrap(spacing: 4, children: [
              TextButton.icon(
                  onPressed: c.busy ? null : () => c.call(contact.phone),
                  icon: const Icon(Icons.call_outlined),
                  label: const Text('Позвонить')),
              TextButton.icon(
                  onPressed: c.busy ? null : () => c.composeSms(contact),
                  icon: const Icon(Icons.sms_outlined),
                  label: const Text('SMS SOS')),
              IconButton(
                  tooltip: 'Изменить',
                  onPressed:
                      c.busy ? null : () => editContact(context, c, contact),
                  icon: const Icon(Icons.edit_outlined)),
              IconButton(
                  tooltip: 'Удалить',
                  onPressed: c.busy
                      ? null
                      : () async {
                          final remove = await showDialog<bool>(
                              context: context,
                              builder: (ctx) => AlertDialog(
                                      title: const Text('Удалить контакт?'),
                                      content: Text(
                                          '${contact.name} больше не будет получать новые SOS.'),
                                      actions: [
                                        TextButton(
                                            onPressed: () =>
                                                Navigator.pop(ctx, false),
                                            child: const Text('Отмена')),
                                        TextButton(
                                            onPressed: () =>
                                                Navigator.pop(ctx, true),
                                            child: const Text('Удалить'))
                                      ]));
                          if (remove == true) c.deleteContact(contact);
                        },
                  icon: const Icon(Icons.delete_outline)),
            ]),
          ])),
        const SizedBox(height: 8),
        const Text(
            'SMS открывается в приложении сообщений. Отправку подтверждаете вы.',
            style: TextStyle(color: QorgoDesign.muted)),
      ]);
  List<Widget> _incoming(Snapshot data, {bool includeResolved = false}) {
    final incoming = data.incoming
        .where((v) => includeResolved || v.alert.resolvedAt == null);
    if (incoming.isEmpty) return [];
    return [
      _heading('Близким нужна помощь'),
      for (final item in incoming)
        _card(Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          Text('${item.senderName}: ${item.alert.title}',
              style:
                  const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          Text(timeLabel(item.alert.createdAt)),
          if (item.alert.resolvedAt != null)
            const Text('Отправитель завершил тревогу'),
          if (item.alert.location != null)
            TextButton.icon(
                onPressed: c.busy
                    ? null
                    : () => _showMap(
                        item.alert.location!, 'SOS: ${item.senderName}'),
                icon: const Icon(Icons.map_outlined),
                label: const Text('Место SOS')),
          if (item.acknowledged)
            const Text('Вы подтвердили: помогаю')
          else if (item.alert.resolvedAt == null)
            FilledButton(
                onPressed: c.busy ? null : () => c.acknowledge(item.deliveryId),
                child: const Text('Помогаю — подтвердить SOS')),
        ])),
    ];
  }

  Widget _events(Snapshot data) =>
      Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        ..._incoming(data, includeResolved: true),
        _heading('История событий'),
        if (data.alerts.isEmpty && data.journeys.isEmpty)
          _card(const Text(
              'Событий пока нет. SOS и сопровождения сохраняются автоматически.')),
        for (final alert in data.alerts) _alertCard(alert, expanded: true),
        if (data.journeys.isNotEmpty) _heading('Сопровождения'),
        for (final journey in data.journeys)
          _card(Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(journey.destination,
                style: const TextStyle(fontWeight: FontWeight.bold)),
            Text(journey.label),
            Text('До ${timeLabel(journey.deadline)}'),
          ])),
      ]);
  Widget _profile(Snapshot data) =>
      Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        _heading('Мой профиль'),
        _card(Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(data.profile.name,
              style:
                  const TextStyle(fontSize: 22, fontWeight: FontWeight.w600)),
          Text(data.profile.email),
          const SizedBox(height: 8),
          Text(data.profile.phone.isEmpty
              ? 'Номер телефона не указан'
              : data.profile.phone),
          if (data.profile.phone.isEmpty)
            const Text(
                'Добавьте свой номер, чтобы близкие могли найти вас в QORGO.',
                style: TextStyle(color: QorgoDesign.muted, fontSize: 13)),
          TextButton(
              onPressed: c.busy
                  ? null
                  : () async {
                      final profile = await showDialog<Profile>(
                          context: context,
                          builder: (_) =>
                              _ProfileDialog(initial: data.profile));
                      if (profile != null) {
                        c.saveProfile(profile.name, phone: profile.phone);
                      }
                    },
              child: const Text('Изменить профиль')),
        ])),
        _card(SwitchListTile(
          contentPadding: EdgeInsets.zero,
          title: const Text('Непрерывная защита',
              style: TextStyle(fontWeight: FontWeight.w600)),
          subtitle: Text(c.continuousProtection
              ? (c.lastLocationSent == null
                  ? 'Ожидаем разрешение геолокации'
                  : 'Активна · последнее обновление ${timeLabel(c.lastLocationSent!)}')
              : 'Приостановлена. SOS продолжит запрашивать координаты.'),
          value: c.continuousProtection,
          onChanged: c.busy ? null : c.setContinuousProtection,
        )),
        _card(ListTile(
          leading: const Icon(Icons.lock_outline, color: QorgoDesign.accent),
          title: const Text('SOS на экране блокировки'),
          subtitle: const Text(
              'Добавьте быстрый доступ QORGO SOS. Нажатие всегда попросит подтвердить вызов.'),
          trailing: FilledButton(
              onPressed: _addSosShortcut, child: const Text('Добавить')),
        )),
        const Text(
            'Координаты хранятся до 30 дней. Отключить защиту можно в любой момент.',
            style: TextStyle(fontSize: 12, color: QorgoDesign.muted)),
        const SizedBox(height: 20),
        OutlinedButton(
            onPressed: c.busy ? null : c.logout,
            child: const Text('Выйти из аккаунта')),
      ]);
  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const QorgoBrand(size: 24), actions: [
          IconButton(
              tooltip: 'Обновить',
              onPressed: c.busy ? null : c.refresh,
              icon: const Icon(Icons.refresh))
        ]),
        body: SafeArea(
            bottom: false,
            child: Column(children: [
              if (c.busy) const LinearProgressIndicator(),
              if (c.error != null)
                Material(
                    color: Theme.of(context).colorScheme.errorContainer,
                    child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Row(children: [
                          Expanded(child: Text(c.error!)),
                          TextButton(
                              onPressed: c.busy ? null : c.refresh,
                              child: const Text('Обновить'))
                        ]))),
              Expanded(
                  child: c.snapshot == null
                      ? Center(
                          child: FilledButton(
                              onPressed: c.busy ? null : c.refresh,
                              child: const Text('Загрузить данные')))
                      : RefreshIndicator(
                          onRefresh: c.refresh,
                          child: Center(
                              child: ConstrainedBox(
                            constraints: const BoxConstraints(maxWidth: 560),
                            child: ListView(
                                physics: const AlwaysScrollableScrollPhysics(),
                                padding:
                                    const EdgeInsets.fromLTRB(20, 20, 20, 24),
                                children: [
                                  switch (_tab) {
                                    0 => _home(c.snapshot!),
                                    1 => _contacts(c.snapshot!),
                                    2 => _events(c.snapshot!),
                                    _ => _profile(c.snapshot!)
                                  },
                                  const SizedBox(height: 16),
                                  if (_tab != 0 && c.syncedAt != null)
                                    Text('Обновлено ${timeLabel(c.syncedAt!)}',
                                        textAlign: TextAlign.center,
                                        style: const TextStyle(
                                            fontSize: 12,
                                            color: QorgoDesign.muted)),
                                ]),
                          )))),
            ])),
        bottomNavigationBar: QorgoBottomNavBar(
          selectedIndex: _tab,
          onSelected: (value) => setState(() => _tab = value),
        ),
      );
}

class _ProfileDialog extends StatefulWidget {
  const _ProfileDialog({required this.initial});
  final Profile initial;
  @override
  State<_ProfileDialog> createState() => _ProfileDialogState();
}

class _ProfileDialogState extends State<_ProfileDialog> {
  final _form = GlobalKey<FormState>();
  late final TextEditingController _name, _phone;
  @override
  void initState() {
    super.initState();
    _name = TextEditingController(text: widget.initial.name);
    _phone = TextEditingController(text: widget.initial.phone);
  }

  @override
  void dispose() {
    _name.dispose();
    _phone.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => AlertDialog(
        title: const Text('Мой профиль'),
        content: SingleChildScrollView(
            child: Form(
                key: _form,
                child: Column(mainAxisSize: MainAxisSize.min, children: [
                  TextFormField(
                      controller: _name,
                      maxLength: 100,
                      decoration: const InputDecoration(labelText: 'Имя'),
                      validator: (value) =>
                          value!.trim().isEmpty ? 'Укажите имя' : null),
                  const SizedBox(height: 12),
                  TextFormField(
                      controller: _phone,
                      keyboardType: TextInputType.phone,
                      decoration: const InputDecoration(
                          labelText: 'Номер телефона',
                          hintText: '+996700123456',
                          helperText:
                              'Близкие смогут найти вас по этому номеру',
                          helperMaxLines: 2),
                      validator: (value) {
                        if (value!.trim().isEmpty) return null;
                        try {
                          normalizeContactPhone(value);
                          return null;
                        } on QorgoException catch (e) {
                          return e.message;
                        }
                      }),
                ]))),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Отмена')),
          FilledButton(
              onPressed: () {
                if (_form.currentState!.validate()) {
                  Navigator.pop(
                      context,
                      Profile(
                          name: _name.text.trim(),
                          email: widget.initial.email,
                          phone: _phone.text.trim().isEmpty
                              ? ''
                              : normalizeContactPhone(_phone.text)));
                }
              },
              child: const Text('Сохранить')),
        ],
      );
}
