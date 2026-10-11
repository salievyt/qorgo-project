import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:qorgo/data/api_client.dart';
import 'package:qorgo/data/remote_repository.dart';
import 'package:qorgo/domain/entities.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  test(
      'SOS retains idempotency key through a network failure and application restart',
      () async {
    FlutterSecureStorage.setMockInitialValues(
        {'qorgo.auth.token': 'test-token'});
    final keys = <String>[];
    var failed = false;
    final client = MockClient((request) async {
      expect(request.headers['Authorization'], 'Token test-token');
      final body = jsonDecode(request.body);
      keys.add(body['request_id']);
      if (!failed) {
        failed = true;
        throw http.ClientException('offline');
      }
      return http.Response(
          jsonEncode({
            'id': 1,
            'created_at': DateTime.now().toIso8601String(),
            'reason': 'sos',
            'resolved_at': null,
            'latitude': null,
            'deliveries': []
          }),
          201);
    });
    RemoteSafetyRepository makeRepository() => RemoteSafetyRepository(
        ApiClient('https://example.invalid/api', client: client),
        const FlutterSecureStorage());
    final first = makeRepository();
    await first.restoreSession();
    await expectLater(first.activateSos(null), throwsA(isA<QorgoException>()));
    final restarted = makeRepository();
    await restarted.restoreSession();
    await restarted.activateSos(null);
    expect(keys, hasLength(2));
    expect(keys[0], keys[1]);
  });
  test('HTTP 401 has an explicit session-expired error', () async {
    final api = ApiClient('https://example.invalid/api',
        client: MockClient(
            (_) async => http.Response('{"detail":"Expired"}', 401)));
    await expectLater(
        api.request('GET', 'profile/'),
        throwsA(isA<QorgoException>()
            .having((e) => e.unauthorized, 'unauthorized', true)));
  });
}
