import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:qorgo/feature/app/app_view.dart';
import 'package:qorgo/feature/app/app_view_model.dart';
import 'package:qorgo/feature/app/splash_view.dart';
import 'support/fakes.dart';

void main() {
  testWidgets(
      'Splash waits for session initialization and then opens the account screen',
      (tester) async {
    final vm =
        AppViewModel(FakeRepository()..authenticated = false, FakeDevice());
    await tester.pumpWidget(QorgoApp(controller: vm));
    expect(find.byType(SplashView), findsOneWidget);
    await tester.pump(const Duration(seconds: 2));
    expect(find.byType(SplashView), findsOneWidget);
    await vm.initialize();
    await tester.pumpAndSettle();
    expect(find.byType(SplashView), findsNothing);
    expect(find.text('Создать аккаунт'), findsOneWidget);
    await tester.pumpWidget(const SizedBox());
    vm.dispose();
  });
}
