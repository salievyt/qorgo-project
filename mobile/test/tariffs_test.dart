import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:qorgo/presentation/tariffs_screen.dart';

void main() {
  testWidgets('Tariffs show complete annual prices on a narrow phone',
      (tester) async {
    tester.view.physicalSize = const Size(320, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(const MaterialApp(home: TariffsScreen()));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Год · экономия 17%'));
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(find.text('1990 сом / год'), 250,
        scrollable: find.byType(Scrollable).first);
    expect(find.text('≈ 166 сом/месяц · оплата за год целиком'), findsOneWidget);
    expect(tester.takeException(), isNull);
    await tester.scrollUntilVisible(find.text('3490 сом / год'), 250,
        scrollable: find.byType(Scrollable).first);
    expect(find.text('≈ 291 сом/месяц · оплата за год целиком'), findsOneWidget);
    expect(tester.takeException(), isNull);
    expect(find.byType(FilledButton), findsNothing);
  });
}
