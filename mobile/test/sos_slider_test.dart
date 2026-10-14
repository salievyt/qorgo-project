import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:qorgo/core/widgets/sos_slider.dart';

void main() {
  Future<void> mount(WidgetTester tester, VoidCallback activate) =>
      tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Center(
              child: SizedBox(
                width: 320,
                child: SosSlider(onActivate: activate),
              ),
            ),
          ),
        ),
      );
  testWidgets('Tap and incomplete or cancelled drags do not activate SOS', (
    tester,
  ) async {
    var calls = 0;
    await mount(tester, () => calls++);
    final thumb = find.byKey(const Key('sos-thumb'));
    await tester.tap(thumb);
    await tester.drag(thumb, const Offset(100, 0));
    await tester.pump();
    expect(calls, 0);
    final gesture = await tester.startGesture(tester.getCenter(thumb));
    await gesture.moveBy(const Offset(100, 0));
    await gesture.cancel();
    await tester.pump();
    expect(calls, 0);
    expect(tester.getTopLeft(thumb).dx, 248);
  });
  testWidgets('Reaching the end activates once before release', (tester) async {
    var calls = 0;
    await mount(tester, () => calls++);
    final gesture = await tester.startGesture(
      tester.getCenter(find.byKey(const Key('sos-thumb'))),
    );
    await gesture.moveBy(const Offset(30, 0));
    await gesture.moveBy(const Offset(300, 0));
    expect(calls, 1);
    await gesture.moveBy(const Offset(-100, 0));
    await gesture.moveBy(const Offset(100, 0));
    expect(calls, 1);
    await gesture.up();
  });
}
