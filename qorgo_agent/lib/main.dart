import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:url_launcher/url_launcher.dart';

import 'core/design.dart';
import 'data/agent_repository.dart';
import 'domain/incident.dart';
import 'feature/agent_view_model.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final vm = AgentViewModel(HttpIncidentRepository());
  runApp(AgentApp(vm: vm));
  await vm.initialize();
}

class AgentApp extends StatelessWidget {
  const AgentApp({super.key, required this.vm});
  final AgentViewModel vm;
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'QORGO AGENT',
    debugShowCheckedModeBanner: false,
    theme: AgentDesign.theme,
    home: AnimatedBuilder(
      animation: vm,
      builder: (_, _) => !vm.ready
          ? const _Splash()
          : vm.signedIn
          ? _Queue(vm: vm)
          : _Login(vm: vm),
    ),
  );
}

class _Brand extends StatelessWidget {
  const _Brand();
  @override
  Widget build(BuildContext context) => Row(
    mainAxisSize: MainAxisSize.min,
    children: [
      SvgPicture.asset('assets/brand/qorgo-light.svg', width: 29, height: 36),
      const SizedBox(width: 5),
      const Text(
        'QORGO',
        style: TextStyle(
          fontSize: 25,
          fontWeight: FontWeight.w600,
          letterSpacing: -1,
        ),
      ),
      const Padding(
        padding: EdgeInsets.only(left: 8),
        child: Text(
          'AGENT',
          style: TextStyle(
            fontSize: 11,
            letterSpacing: 1.7,
            color: AgentDesign.accent,
          ),
        ),
      ),
    ],
  );
}

class _Splash extends StatelessWidget {
  const _Splash();
  @override
  Widget build(BuildContext context) =>
      const Scaffold(body: Center(child: _Brand()));
}

class _Login extends StatefulWidget {
  const _Login({required this.vm});
  final AgentViewModel vm;
  @override
  State<_Login> createState() => _LoginState();
}

class _LoginState extends State<_Login> {
  final form = GlobalKey<FormState>();
  final phone = TextEditingController();
  final password = TextEditingController();
  @override
  void dispose() {
    phone.dispose();
    password.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 420),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const _Brand(),
                const SizedBox(height: 56),
                const Text(
                  'Рабочее место\nоператора',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.w600,
                    height: 1.1,
                  ),
                ),
                const SizedBox(height: 12),
                const Text(
                  'Принимайте сигналы SOS и координируйте помощь.',
                  style: TextStyle(color: AgentDesign.muted),
                ),
                const SizedBox(height: 32),
                Form(
                  key: form,
                  child: Column(
                    children: [
                      TextFormField(
                        controller: phone,
                        keyboardType: TextInputType.phone,
                        decoration: const InputDecoration(
                          labelText: 'Рабочий номер',
                        ),
                        validator: (v) =>
                            v!.trim().isEmpty ? 'Укажите номер' : null,
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: password,
                        obscureText: true,
                        decoration: const InputDecoration(labelText: 'Пароль'),
                        validator: (v) => v!.isEmpty ? 'Укажите пароль' : null,
                      ),
                    ],
                  ),
                ),
                if (widget.vm.error != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 16),
                    child: Text(
                      widget.vm.error!,
                      style: const TextStyle(color: AgentDesign.danger),
                    ),
                  ),
                const SizedBox(height: 24),
                FilledButton(
                  onPressed: widget.vm.busy
                      ? null
                      : () {
                          if (form.currentState!.validate()) {
                            widget.vm.login(phone.text, password.text);
                          }
                        },
                  child: Text(
                    widget.vm.busy
                        ? 'Проверяем доступ...'
                        : 'Войти как оператор',
                  ),
                ),
                const SizedBox(height: 16),
                const Text(
                  'Доступ выдаёт администратор QORGO.',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 12, color: AgentDesign.muted),
                ),
              ],
            ),
          ),
        ),
      ),
    ),
  );
}

class _Queue extends StatelessWidget {
  const _Queue({required this.vm});
  final AgentViewModel vm;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: const _Brand(),
      actions: [
        IconButton(
          onPressed: vm.busy ? null : vm.refresh,
          icon: const Icon(Icons.refresh),
        ),
        IconButton(onPressed: vm.logout, icon: const Icon(Icons.logout)),
      ],
    ),
    body: SafeArea(
      child: RefreshIndicator(
        onRefresh: vm.refresh,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Row(
              children: [
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Очередь SOS',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        'Активные инциденты',
                        style: TextStyle(color: AgentDesign.muted),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 8,
                  ),
                  decoration: BoxDecoration(
                    color: vm.incidents.isEmpty
                        ? AgentDesign.surface
                        : AgentDesign.danger.withValues(alpha: .18),
                    borderRadius: BorderRadius.circular(18),
                  ),
                  child: Text(
                    '${vm.incidents.length} активных',
                    style: TextStyle(
                      fontSize: 12,
                      color: vm.incidents.isEmpty
                          ? AgentDesign.muted
                          : AgentDesign.danger,
                    ),
                  ),
                ),
              ],
            ),
            if (vm.error != null) _Error(vm.error!),
            const SizedBox(height: 24),
            if (vm.incidents.isEmpty)
              const _Empty()
            else
              for (final item in vm.incidents) _Incident(item: item, vm: vm),
          ],
        ),
      ),
    ),
  );
}

class _Error extends StatelessWidget {
  const _Error(this.text);
  final String text;
  @override
  Widget build(BuildContext context) => Container(
    margin: const EdgeInsets.only(top: 18),
    padding: const EdgeInsets.all(14),
    decoration: BoxDecoration(
      color: AgentDesign.danger.withValues(alpha: .12),
      borderRadius: BorderRadius.circular(12),
    ),
    child: Text(text, style: const TextStyle(color: AgentDesign.danger)),
  );
}

class _Empty extends StatelessWidget {
  const _Empty();
  @override
  Widget build(BuildContext context) => const Card(
    child: Padding(
      padding: EdgeInsets.all(28),
      child: Column(
        children: [
          Icon(Icons.shield_outlined, size: 38, color: AgentDesign.accent),
          SizedBox(height: 14),
          Text(
            'Активных сигналов нет',
            style: TextStyle(fontSize: 17, fontWeight: FontWeight.w600),
          ),
          SizedBox(height: 6),
          Text(
            'Очередь обновляется автоматически.',
            style: TextStyle(color: AgentDesign.muted),
          ),
        ],
      ),
    ),
  );
}

class _Incident extends StatelessWidget {
  const _Incident({required this.item, required this.vm});
  final Incident item;
  final AgentViewModel vm;
  Future<void> map() => launchUrl(
    Uri.parse(
      'https://www.openstreetmap.org/?mlat=${item.latitude}&mlon=${item.longitude}#map=16/${item.latitude}/${item.longitude}',
    ),
    mode: LaunchMode.externalApplication,
  );
  Future<void> close(BuildContext context) async {
    final note = TextEditingController();
    final value = await showModalBottomSheet<String>(
      context: context,
      builder: (ctx) => Padding(
        padding: const EdgeInsets.fromLTRB(24, 8, 24, 30),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Закрыть инцидент',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: note,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'Комментарий для журнала',
              ),
            ),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: () => Navigator.pop(ctx, 'resolved'),
              child: const Text('Помощь оказана'),
            ),
            TextButton(
              onPressed: () => Navigator.pop(ctx, 'false_alarm'),
              child: const Text('Ложный вызов'),
            ),
          ],
        ),
      ),
    );
    if (value != null) vm.close(item.id, value, note.text.trim());
  }

  @override
  Widget build(BuildContext context) {
    final mins = DateTime.now().difference(item.startedAt.toLocal()).inMinutes;
    final taken = item.assignedTo.isNotEmpty;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Container(
                  width: 9,
                  height: 9,
                  decoration: const BoxDecoration(
                    color: AgentDesign.danger,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  'SOS · ${mins < 1 ? 'только что' : '$mins мин назад'}',
                  style: const TextStyle(
                    fontSize: 12,
                    color: AgentDesign.danger,
                  ),
                ),
                const Spacer(),
                if (taken)
                  const Text(
                    'В работе',
                    style: TextStyle(fontSize: 12, color: AgentDesign.accent),
                  ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              item.name,
              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w600),
            ),
            if (item.address.isNotEmpty)
              Text(
                item.address,
                style: const TextStyle(color: AgentDesign.muted),
              ),
            const SizedBox(height: 14),
            Text(
              '${item.latitude.toStringAsFixed(5)}, ${item.longitude.toStringAsFixed(5)} · ${item.battery.round()}%',
              style: const TextStyle(color: AgentDesign.muted),
            ),
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: map,
              icon: const Icon(Icons.map_outlined),
              label: const Text('Открыть карту'),
            ),
            const SizedBox(height: 8),
            FilledButton(
              onPressed: vm.busy
                  ? null
                  : () => taken ? close(context) : vm.take(item.id),
              child: Text(taken ? 'Завершить инцидент' : 'Принять в работу'),
            ),
          ],
        ),
      ),
    );
  }
}
