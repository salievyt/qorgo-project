import 'package:flutter/material.dart';
import 'app_controller.dart';

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key, required this.controller});
  final AppController controller;
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
        child: ListView(padding: const EdgeInsets.all(28), children: [
          const SizedBox(height: 40),
          const Icon(Icons.shield_outlined, size: 56, color: Color(0xFF176B54)),
          const SizedBox(height: 20),
          const Text('QORGO',
              textAlign: TextAlign.center,
              style: TextStyle(
                  fontSize: 32, fontWeight: FontWeight.w900, letterSpacing: 4)),
          const SizedBox(height: 8),
          Text(
              _register
                  ? 'Создайте свой круг безопасности'
                  : 'Войдите в свой аккаунт',
              textAlign: TextAlign.center),
          const SizedBox(height: 36),
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
