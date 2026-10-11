import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:qorgo/data/api_client.dart';
import 'package:qorgo/data/device_gateway.dart';
import 'package:qorgo/data/remote_repository.dart';
import 'package:qorgo/presentation/app_controller.dart';
import 'package:qorgo/presentation/app_shell.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets(
      'Real API, Keychain, contact form, journey and SOS survive session restore',
      (tester) async {
    const storage = FlutterSecureStorage();
    final api = ApiClient('http://127.0.0.1:8000/api');
    final repository = RemoteSafetyRepository(api, storage);
    final controller = AppController(repository, NativeDeviceGateway());
    await controller.initialize();
    if (controller.signedIn) await controller.logout();
    await tester.pumpWidget(QorgoApp(controller: controller));
    final email =
        'integration-${DateTime.now().microsecondsSinceEpoch}@example.invalid';
    final fields = find.byType(TextFormField);
    await tester.enterText(fields.at(0), 'MVP Test');
    await tester.enterText(fields.at(1), email);
    await tester.enterText(fields.at(2), 'Qorgo-Integration-82-Strong!');
    await tester.tap(find.text('Создать аккаунт'));
    for (var i = 0; i < 100 && controller.busy; i++) {
      await tester.pump(const Duration(milliseconds: 100));
    }
    await tester.pumpAndSettle();
    expect(controller.signedIn, true, reason: controller.error);
    expect(controller.snapshot?.profile.email, email);
    await tester.tap(find.text('Близкие'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Добавить близкого'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextFormField).at(0), 'MVP Contact');
    await tester.enterText(find.byType(TextFormField).at(1), '+996700000000');
    await tester.ensureVisible(find.text('Сохранить'));
    await tester.tap(find.text('Сохранить'));
    for (var i = 0; i < 100 && controller.busy; i++) {
      await tester.pump(const Duration(milliseconds: 100));
    }
    await tester.pumpAndSettle();
    expect(find.text('MVP Contact'), findsOneWidget);
    expect(controller.snapshot!.contacts.single.phone, '+996700000000');
    expect(await controller.startJourney('Home', 5), true,
        reason: controller.error);
    final journey = controller.activeJourney!;
    expect(await controller.finishJourney(journey, true), true,
        reason: controller.error);
    expect(controller.snapshot!.journeys.first.state, 'arrived');
    // No native location prompt and no real contacts/provider in this test.
    final alert = await repository.activateSos(null);
    expect(alert.deliveries.single.name, 'MVP Contact');
    final restored =
        RemoteSafetyRepository(ApiClient('http://127.0.0.1:8000/api'), storage);
    expect(await restored.restoreSession(), true);
    final persisted = await restored.load();
    expect(persisted.contacts.single.name, 'MVP Contact');
    expect(persisted.alerts.first.id, alert.id);
    expect(persisted.journeys.first.state, 'arrived');
    expect(persisted.deliveryReady, false);
    await repository.resolveAlert(alert.id);
    await controller.logout();
    await tester.pumpWidget(const SizedBox());
    controller.dispose();
    api.client.close();
  });
}
