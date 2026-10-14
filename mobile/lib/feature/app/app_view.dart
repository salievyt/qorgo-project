import 'package:flutter/material.dart';
import '../../core/design/qorgo_theme.dart';
import 'app_view_model.dart';
import '../auth/auth_view.dart';
import '../safety/safety_view.dart';

class QorgoApp extends StatelessWidget {
  const QorgoApp({super.key, required this.controller});
  final AppViewModel controller;
  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'QORGO',
        debugShowCheckedModeBanner: false,
        theme: QorgoDesign.theme,
        home: ListenableBuilder(
            listenable: controller,
            builder: (context, _) {
              if (!controller.initialized) {
                return const Scaffold(
                    body: Center(child: CircularProgressIndicator()));
              }
              return controller.signedIn
                  ? SafetyView(controller: controller)
                  : AuthScreen(controller: controller);
            }),
      );
}
