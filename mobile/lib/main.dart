import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'core/network/api_client.dart';
import 'core/config/environment.dart';
import 'data/device_gateway.dart';
import 'data/remote_repository.dart';
import 'feature/app/app_view_model.dart';
import 'feature/app/app_view.dart';
export 'feature/app/app_view.dart' show QorgoApp;

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  final controller = AppViewModel(
    RemoteSafetyRepository(
        ApiClient(Environment.apiUrl), const FlutterSecureStorage()),
    NativeDeviceGateway(),
  );
  runApp(QorgoApp(controller: controller));
  await controller.initialize();
}
