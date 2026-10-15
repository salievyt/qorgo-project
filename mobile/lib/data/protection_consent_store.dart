import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Persists the one-time protection explanation independently of a session.
class ProtectionConsentStore {
  ProtectionConsentStore({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage();
  static const _key = 'qorgo.continuous_protection.explained.v1';
  final FlutterSecureStorage _storage;

  Future<bool> shouldExplain() async => await _storage.read(key: _key) == null;
  Future<void> markExplained() => _storage.write(key: _key, value: 'true');
}
