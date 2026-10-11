import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'data/api_client.dart';
import 'data/device_gateway.dart';
import 'data/remote_repository.dart';
import 'presentation/app_controller.dart';
import 'presentation/app_shell.dart';
export 'presentation/app_shell.dart' show QorgoApp;

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  const apiUrl = String.fromEnvironment('QORGO_API_URL',
      defaultValue: 'http://127.0.0.1:8000/api');
  final controller = AppController(
    RemoteSafetyRepository(ApiClient(apiUrl), const FlutterSecureStorage()),
    NativeDeviceGateway(),
  );
  runApp(QorgoApp(controller: controller));
  await controller.initialize();
}
