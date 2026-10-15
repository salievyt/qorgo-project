import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:qorgo/feature/app/app_view_model.dart';
import 'package:qorgo/feature/app/app_view.dart';
import 'support/fakes.dart';

void main() {
  testWidgets('Home and contact form fit a narrow phone and save actual input',
      (tester) async {
    tester.view.physicalSize = const Size(360, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    final repository = FakeRepository();
    final controller = AppViewModel(repository, FakeDevice());
    await controller.initialize();
    await tester.pumpWidget(
        QorgoApp(controller: controller, splashDuration: Duration.zero));
    await tester.pump();
    if (find.text('Не сейчас').evaluate().isNotEmpty) {
      await tester.tap(find.text('Не сейчас'));
      await tester.pumpAndSettle();
    }
    expect(find.text('Нужна помощь?'), findsOneWidget);
    expect(tester.takeException(), isNull);
    await tester.tap(find.text('Близкие'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Добавить близкого'));
    await tester.pumpAndSettle();
    final fields = find.byType(TextFormField);
    await tester.enterText(fields.at(0), 'Мама');
    await tester.enterText(fields.at(1), '+996700000000');
    await tester.tap(find.text('Сохранить'));
    await tester.pumpAndSettle();
    expect(repository.contacts.single.name, 'Мама');
    expect(find.text('Мама'), findsOneWidget);
    expect(find.text('ДЕМО'), findsNothing);
    expect(tester.takeException(), isNull);
    await tester.pumpWidget(const SizedBox());
    controller.dispose();
  });
  testWidgets('New installation presents real account registration',
      (tester) async {
    final repository = FakeRepository()..authenticated = false;
    final controller = AppViewModel(repository, FakeDevice());
    await controller.initialize();
    await tester.pumpWidget(
        QorgoApp(controller: controller, splashDuration: Duration.zero));
    await tester.pump();
    if (find.text('Не сейчас').evaluate().isNotEmpty) {
      await tester.tap(find.text('Не сейчас'));
      await tester.pumpAndSettle();
    }
    expect(find.text('Создать аккаунт'), findsOneWidget);
    expect(find.text('ДЕМО'), findsNothing);
    await tester.pumpWidget(const SizedBox());
    controller.dispose();
  });
}
