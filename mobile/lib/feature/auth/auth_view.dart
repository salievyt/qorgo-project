import '../../core/design/qorgo_brand.dart';
import '../../core/design/qorgo_theme.dart';
import 'package:flutter/material.dart';
import '../app/app_view_model.dart';

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key, required this.controller});
  final AppViewModel controller;
  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final _form = GlobalKey<FormState>();
  final _email = TextEditingController(),
      _password = TextEditingController(),
      _name = TextEditingController();
  bool _register = true;
  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    _name.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
          body: SafeArea(
              child: Center(
                  child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 480),
        child: ListView(padding: const EdgeInsets.all(24), children: [
          const SizedBox(height: 32),
          const Center(child: QorgoBrand(center: true)),
          const SizedBox(height: 48),
          Text(_register ? 'Ваш круг безопасности' : 'С возвращением',
              style: const TextStyle(
                  fontSize: 30,
                  height: 1.15,
                  fontWeight: FontWeight.w600,
                  letterSpacing: -1)),
          const SizedBox(height: 12),
          Text(
              _register
                  ? 'Создайте аккаунт, чтобы быть на связи с близкими.'
                  : 'Войдите, чтобы быть на связи с близкими.',
              style: const TextStyle(
                  fontSize: 14, height: 1.5, color: QorgoDesign.muted)),
          const SizedBox(height: 28),
          Form(
              key: _form,
              child: Column(children: [
                if (_register)
                  TextFormField(
                      controller: _name,
                      textCapitalization: TextCapitalization.words,
                      decoration: const InputDecoration(labelText: 'Ваше имя'),
                      validator: (v) =>
                          v!.trim().isEmpty ? 'Укажите имя' : null),
                const SizedBox(height: 14),
                TextFormField(
                    controller: _email,
                    keyboardType: TextInputType.emailAddress,
                    autocorrect: false,
                    decoration: const InputDecoration(labelText: 'Email'),
                    validator: (v) =>
                        !RegExp(r'^\S+@\S+\.\S+$').hasMatch(v!.trim())
                            ? 'Проверьте email'
                            : null),
                const SizedBox(height: 14),
                TextFormField(
                    controller: _password,
                    obscureText: true,
                    autocorrect: false,
                    decoration: const InputDecoration(labelText: 'Пароль'),
                    validator: (v) =>
                        v!.length < 8 ? 'Минимум 8 символов' : null),
              ])),
          const SizedBox(height: 20),
          if (widget.controller.error != null)
            Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: Text(widget.controller.error!,
                    style:
                        TextStyle(color: Theme.of(context).colorScheme.error))),
          FilledButton(
              onPressed: widget.controller.busy
                  ? null
                  : () {
                      if (_form.currentState!.validate()) {
                        widget.controller.authenticate(
                            _email.text, _password.text,
                            name: _register ? _name.text : null);
                      }
                    },
              child: Text(widget.controller.busy
                  ? 'Подключаемся…'
                  : _register
                      ? 'Создать аккаунт'
                      : 'Войти')),
          TextButton(
              onPressed: widget.controller.busy
                  ? null
                  : () => setState(() => _register = !_register),
              child: Text(
                  _register ? 'Уже есть аккаунт? Войти' : 'Создать аккаунт')),
        ]),
      ))));
}
