import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:qorgo/core/network/api_client.dart';
import 'package:qorgo/core/widgets/sos_slider.dart';
import 'package:qorgo/data/device_gateway.dart';
import 'package:qorgo/data/remote_repository.dart';
import 'package:qorgo/domain/entities.dart';
import 'package:qorgo/feature/app/app_view_model.dart';
import 'package:qorgo/feature/app/app_view.dart';

class TestLocationDevice extends NativeDeviceGateway {
  @override
  Future<GeoPoint> locate() async => GeoPoint(42.87, 74.60, 10, DateTime.now());
}

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets(
      'Public HTTPS API: slider SOS reaches another account and is acknowledged',
      (tester) async {
    const url = String.fromEnvironment('QORGO_API_URL',
        defaultValue: 'https://api.qorgo.services/api');
    final senderApi = ApiClient(url);
    final receiverApi = ApiClient(url);
    const password = 'Qorgo-Integration-82-Strong!';
    final suffix = DateTime.now().microsecondsSinceEpoch;
    final receiverEmail = 'mvp-receiver-$suffix@example.invalid';
    final account = await receiverApi.request('POST', 'register/', {
      'name': 'MVP Receiver',
      'email': receiverEmail,
      'password': password,
    });
    receiverApi.token = account['token'];
    final sender =
        RemoteSafetyRepository(senderApi, const FlutterSecureStorage());
    final receiver =
        RemoteSafetyRepository(receiverApi, const FlutterSecureStorage());
    final vm = AppViewModel(sender, TestLocationDevice());
    await vm.initialize();
    if (vm.signedIn) await vm.logout();
    expect(
        await vm.authenticate('mvp-sender-$suffix@example.invalid', password,
            name: 'MVP Sender'),
        true,
        reason: vm.error);
    expect(
        await vm.saveContact(Contact(
            name: 'MVP Receiver',
            phone: '+996700000000',
            email: receiverEmail)),
        true,
        reason: vm.error);
    await tester
        .pumpWidget(QorgoApp(controller: vm, splashDuration: Duration.zero));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.byType(SosSlider));
    await tester.drag(find.byKey(const Key('sos-thumb')), const Offset(500, 0));
    for (var i = 0; i < 300 && vm.busy; i++) {
      await tester.pump(const Duration(milliseconds: 100));
    }
    await tester.pumpAndSettle();
    expect(vm.activeAlert, isNotNull, reason: vm.error);
    final alert = vm.activeAlert!;
    final incoming = (await receiver.load()).incoming.single;
    expect(incoming.alert.id, alert.id);
    expect(incoming.alert.location!.latitude, 42.87);
    expect(incoming.acknowledged, false);
    await receiver.acknowledge(incoming.deliveryId);
    await vm.refresh();
    await tester.pumpAndSettle();
    expect(vm.activeAlert!.deliveries.single.status, 'received');
    expect(find.text('MVP Receiver: Получатель подтвердил SOS в приложении'),
        findsOneWidget);
    expect((await receiver.load()).incoming.single.acknowledged, true);
    await sender.resolveAlert(alert.id);
    await vm.logout();
    await receiverApi.request('POST', 'logout/');
    await tester.pumpWidget(const SizedBox());
    vm.dispose();
    senderApi.client.close();
    receiverApi.client.close();
  });
}
