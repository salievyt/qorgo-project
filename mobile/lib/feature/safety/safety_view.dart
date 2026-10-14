import '../../core/design/qorgo_brand.dart';
import '../../core/design/qorgo_theme.dart';
import 'package:flutter/material.dart';
import '../../domain/entities.dart';
import '../../core/widgets/sos_slider.dart';
import '../app/app_view_model.dart';
import 'forms.dart';
import '../maps/map_view.dart';

String timeLabel(DateTime value) {
  final v = value.toLocal();
  return '${v.day.toString().padLeft(2, '0')}.${v.month.toString().padLeft(2, '0')} ${v.hour.toString().padLeft(2, '0')}:${v.minute.toString().padLeft(2, '0')}';
}

class SafetyView extends StatefulWidget {
  const SafetyView({super.key, required this.controller});
  final AppViewModel controller;
  @override
  State<SafetyView> createState() => _SafetyViewState();
}

class _SafetyViewState extends State<SafetyView> with WidgetsBindingObserver {
  int _tab = 0;
  AppViewModel get c => widget.controller;
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) c.refresh();
  }

  Widget _card(Widget child) => Card(
      elevation: 0,
      color: Colors.white,
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
    return Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
      Text(
          data.profile.name.isEmpty
              ? 'Вы под защитой близких'
              : 'Здравствуйте, ${data.profile.name}',
          style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w600)),
      const SizedBox(height: 12),
      _card(Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          const Icon(Icons.people_outline, color: QorgoDesign.green),
          const SizedBox(width: 12),
          Expanded(
              child: Text('Доверенных контактов: ${data.contacts.length}',
                  style: const TextStyle(fontWeight: FontWeight.bold)))
        ]),
        TextButton(
            onPressed: () => setState(() => _tab = 1),
            child: Text(data.contacts.isEmpty
                ? 'Добавить близкого →'
                : 'Управлять контактами →')),
        if (!data.deliveryReady)
          const Text(
              'Укажите email аккаунта близкого, чтобы он получил SOS в QORGO.',
              style: TextStyle(color: QorgoDesign.muted)),
      ])),
      ..._incoming(data),
      _heading('Нужна помощь?'),
      SosSlider(
          enabled: !c.busy && alert == null && data.contacts.isNotEmpty,
          onActivate: c.activateSos),
      const SizedBox(height: 12),
      Text(
          c.busy
              ? 'Выполняем действие…'
              : data.contacts.isEmpty
                  ? 'Добавьте контакт, чтобы включить SOS'
                  : 'Потяните вправо до конца, чтобы отправить SOS',
          textAlign: TextAlign.center),
      if (alert != null) _alertCard(alert, expanded: true),
      const SizedBox(height: 20),
      _card(Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Моё местоположение',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        const SizedBox(height: 8),
        Text(c.location == null
            ? 'Координаты ещё не определены'
            : '${c.location!.latitude.toStringAsFixed(5)}, ${c.location!.longitude.toStringAsFixed(5)}\nТочность ±${c.location!.accuracy.round()} м • ${timeLabel(c.location!.timestamp)}'),
        Wrap(spacing: 8, children: [
          TextButton.icon(
              onPressed: c.busy ? null : c.updateLocation,
              icon: const Icon(Icons.my_location),
              label: const Text('Определить')),
          if (c.location != null)
            TextButton.icon(
                onPressed: c.busy
                    ? null
                    : () => _showMap(c.location!, 'Моё местоположение'),
                icon: const Icon(Icons.map_outlined),
                label: const Text('На карте')),
        ]),
      ])),
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
          TextButton(
              onPressed: c.busy
                  ? null
                  : () async {
                      final name = await showDialog<String>(
                          context: context,
                          builder: (_) =>
                              _NameDialog(initial: data.profile.name));
                      if (name != null) c.saveProfile(name);
                    },
              child: const Text('Изменить имя')),
        ])),
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
                            padding: const EdgeInsets.all(20),
                            children: [
                              switch (_tab) {
                                0 => _home(c.snapshot!),
                                1 => _contacts(c.snapshot!),
                                2 => _events(c.snapshot!),
                                _ => _profile(c.snapshot!)
                              },
                              const SizedBox(height: 16),
                              if (c.syncedAt != null)
                                Text('Обновлено ${timeLabel(c.syncedAt!)}',
                                    textAlign: TextAlign.center,
                                    style: const TextStyle(
                                        fontSize: 12,
                                        color: QorgoDesign.muted)),
                            ]),
                      )))),
        ])),
        bottomNavigationBar: NavigationBar(
            selectedIndex: _tab,
            onDestinationSelected: (v) => setState(() => _tab = v),
            destinations: const [
              NavigationDestination(
                  icon: Icon(Icons.home_outlined), label: 'Главная'),
              NavigationDestination(
                  icon: Icon(Icons.people_outline), label: 'Близкие'),
              NavigationDestination(
                  icon: Icon(Icons.history), label: 'События'),
              NavigationDestination(
                  icon: Icon(Icons.person_outline), label: 'Профиль'),
            ]),
      );
}

class _NameDialog extends StatefulWidget {
  const _NameDialog({required this.initial});
  final String initial;
  @override
  State<_NameDialog> createState() => _NameDialogState();
}

class _NameDialogState extends State<_NameDialog> {
  late final TextEditingController _name;
  @override
  void initState() {
    super.initState();
    _name = TextEditingController(text: widget.initial);
  }

  @override
  void dispose() {
    _name.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => AlertDialog(
          title: const Text('Ваше имя'),
          content:
              TextField(controller: _name, autofocus: true, maxLength: 100),
          actions: [
            TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Отмена')),
            FilledButton(
                onPressed: () {
                  if (_name.text.trim().isNotEmpty) {
                    Navigator.pop(context, _name.text.trim());
                  }
                },
                child: const Text('Сохранить')),
          ]);
}
