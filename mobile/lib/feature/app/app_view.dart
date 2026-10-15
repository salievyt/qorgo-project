import 'dart:async';
import 'package:flutter/material.dart';
import 'splash_view.dart';
import '../../core/design/qorgo_theme.dart';
import 'app_view_model.dart';
import '../auth/auth_view.dart';
import '../safety/safety_view.dart';

class QorgoApp extends StatefulWidget {
  const QorgoApp(
      {super.key,
      required this.controller,
      this.splashDuration = const Duration(milliseconds: 1200)});
  final AppViewModel controller;
  final Duration splashDuration;
  @override
  State<QorgoApp> createState() => _QorgoAppState();
}

class _QorgoAppState extends State<QorgoApp> {
  Timer? _timer;
  late bool _splashDone;
  @override
  void initState() {
    super.initState();
    _splashDone = widget.splashDuration == Duration.zero;
    if (!_splashDone) {
      _timer = Timer(widget.splashDuration, () {
        if (mounted) setState(() => _splashDone = true);
      });
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  AppViewModel get controller => widget.controller;
  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'QORGO',
        debugShowCheckedModeBanner: false,
        theme: QorgoDesign.theme,
        home: ListenableBuilder(
            listenable: controller,
            builder: (context, _) {
              if (!_splashDone || !controller.initialized) {
                return const SplashView();
              }
              return controller.signedIn
                  ? SafetyView(controller: controller)
                  : AuthScreen(controller: controller);
            }),
      );
}
