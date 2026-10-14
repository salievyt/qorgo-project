import 'package:flutter/material.dart';
import '../../domain/entities.dart';
import '../app/app_view_model.dart';

Future<void> editContact(BuildContext context, AppViewModel controller,
        [Contact? contact]) =>
    showModalBottomSheet(
        context: context,
        isScrollControlled: true,
        useSafeArea: true,
        builder: (_) => ContactForm(controller: controller, contact: contact));

class ContactForm extends StatefulWidget {
  const ContactForm({super.key, required this.controller, this.contact});
  final AppViewModel controller;
  final Contact? contact;
  @override
  State<ContactForm> createState() => _ContactFormState();
}

class _ContactFormState extends State<ContactForm> {
  final _form = GlobalKey<FormState>();
  late final TextEditingController _name, _phone, _email, _relationship;
  bool _saving = false;
  String? _error;
  @override
  void initState() {
    super.initState();
    _name = TextEditingController(text: widget.contact?.name);
    _phone = TextEditingController(text: widget.contact?.phone ?? '+996');
    _email = TextEditingController(text: widget.contact?.email);
    _relationship = TextEditingController(text: widget.contact?.relationship);
  }

  @override
  void dispose() {
    for (final c in [_name, _phone, _email, _relationship]) {
      c.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Padding(
        padding: EdgeInsets.fromLTRB(
            24, 24, 24, MediaQuery.viewInsetsOf(context).bottom + 24),
        child: SingleChildScrollView(
            child: Form(
                key: _form,
                child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                          widget.contact == null
                              ? 'Добавить близкого'
                              : 'Изменить контакт',
                          style: const TextStyle(
                              fontSize: 22, fontWeight: FontWeight.w600)),
                      const SizedBox(height: 20),
                      TextFormField(
                          controller: _name,
                          decoration: const InputDecoration(labelText: 'Имя'),
                          validator: (v) =>
                              v!.trim().isEmpty ? 'Укажите имя' : null),
                      const SizedBox(height: 12),
                      TextFormField(
                          controller: _phone,
                          keyboardType: TextInputType.phone,
                          decoration: const InputDecoration(
                              labelText: 'Телефон с кодом страны'),
                          validator: (v) => RegExp(r'^\+[1-9]\d{7,14}$')
                                  .hasMatch(
                                      v!.replaceAll(RegExp(r'[\s()\-]'), ''))
                              ? null
                              : 'Например +996700123456'),
                      const SizedBox(height: 12),
                      TextFormField(
                          controller: _email,
                          keyboardType: TextInputType.emailAddress,
                          decoration: const InputDecoration(
                              labelText: 'Email аккаунта близкого в QORGO'),
                          validator: (v) => v!.trim().isEmpty ||
                                  RegExp(r'^\S+@\S+\.\S+$').hasMatch(v.trim())
                              ? null
                              : 'Проверьте email'),
                      const SizedBox(height: 12),
                      TextFormField(
                          controller: _relationship,
                          decoration: const InputDecoration(
                              labelText: 'Кем приходится')),
                      const SizedBox(height: 20),
                      if (_error != null)
                        Text(_error!,
                            style: TextStyle(
                                color: Theme.of(context).colorScheme.error)),
                      FilledButton(
                          onPressed: _saving
                              ? null
                              : () async {
                                  if (!_form.currentState!.validate()) return;
                                  setState(() {
                                    _saving = true;
                                    _error = null;
                                  });
                                  final ok = await widget.controller
                                      .saveContact(Contact(
                                          id: widget.contact?.id,
                                          name: _name.text,
                                          phone: _phone.text,
                                          email: _email.text,
                                          relationship: _relationship.text));
                                  if (!context.mounted) return;
                                  if (ok) {
                                    Navigator.pop(context);
                                  } else {
                                    setState(() {
                                      _saving = false;
                                      _error = widget.controller.error;
                                    });
                                  }
                                },
                          child: Text(_saving ? 'Сохраняем…' : 'Сохранить')),
                    ]))),
      );
}

Future<void> startJourney(BuildContext context, AppViewModel controller) =>
    showModalBottomSheet(
        context: context,
        isScrollControlled: true,
        useSafeArea: true,
        builder: (_) => JourneyForm(controller: controller));

class JourneyForm extends StatefulWidget {
  const JourneyForm({super.key, required this.controller});
  final AppViewModel controller;
  @override
  State<JourneyForm> createState() => _JourneyFormState();
}

class _JourneyFormState extends State<JourneyForm> {
  final _form = GlobalKey<FormState>();
  final _destination = TextEditingController(),
      _minutes = TextEditingController(text: '30');
  bool _saving = false;
  String? _error;
  @override
  void dispose() {
    _destination.dispose();
    _minutes.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Padding(
        padding: EdgeInsets.fromLTRB(
            24, 24, 24, MediaQuery.viewInsetsOf(context).bottom + 24),
        child: SingleChildScrollView(
            child: Form(
                key: _form,
                child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text('Я должен добраться',
                          style: TextStyle(
                              fontSize: 22, fontWeight: FontWeight.w600)),
                      const SizedBox(height: 12),
                      const Text(
                          'Если вы не подтвердите прибытие, сервер создаст SOS для ваших контактов. Необходимо настроить сервис отправки.'),
                      const SizedBox(height: 20),
                      TextFormField(
                          controller: _destination,
                          decoration: const InputDecoration(
                              labelText: 'Куда направляетесь?'),
                          validator: (v) =>
                              v!.trim().isEmpty ? 'Укажите место' : null),
                      const SizedBox(height: 12),
                      TextFormField(
                          controller: _minutes,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(
                              labelText: 'Время в минутах'),
                          validator: (v) {
                            final n = int.tryParse(v ?? '');
                            return n == null || n < 1 || n > 1440
                                ? 'От 1 до 1440 минут'
                                : null;
                          }),
                      const SizedBox(height: 20),
                      if (_error != null)
                        Text(_error!,
                            style: TextStyle(
                                color: Theme.of(context).colorScheme.error)),
                      FilledButton(
                          onPressed: _saving
                              ? null
                              : () async {
                                  if (!_form.currentState!.validate()) return;
                                  setState(() => _saving = true);
                                  final ok = await widget.controller
                                      .startJourney(_destination.text,
                                          int.parse(_minutes.text));
                                  if (!context.mounted) return;
                                  if (ok) {
                                    Navigator.pop(context);
                                  } else {
                                    setState(() {
                                      _saving = false;
                                      _error = widget.controller.error;
                                    });
                                  }
                                },
                          child: Text(
                              _saving ? 'Сохраняем…' : 'Начать сопровождение')),
                    ]))),
      );
}
