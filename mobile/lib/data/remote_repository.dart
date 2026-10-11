import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:uuid/uuid.dart';
import '../domain/entities.dart';
import '../domain/repositories.dart';
import 'api_client.dart';

class RemoteSafetyRepository implements SafetyRepository {
  RemoteSafetyRepository(this.api, this.storage);
  final ApiClient api;
  final FlutterSecureStorage storage;
  static const _tokenKey = 'qorgo.auth.token';
  String? _pendingId;
  String get _pendingKey => 'qorgo.sos.pending.${api.token}';
  @override
  Future<bool> restoreSession() async {
    api.token = await storage.read(key: _tokenKey);
    return api.token != null;
  }

  @override
  Future<void> signIn(String email, String password, {String? name}) async {
    final data =
        await api.request('POST', name == null ? 'login/' : 'register/', {
      'email': email.trim(),
      'password': password,
      if (name != null) 'name': name.trim()
    });
    await storage.write(key: _tokenKey, value: data['token']);
    api.token = data['token'];
    _pendingId = null;
  }

  @override
  Future<void> signOut() async {
    try {
      await api.request('POST', 'logout/');
    } finally {
      await storage.delete(key: _tokenKey);
      api.token = null;
      _pendingId = null;
    }
  }

  @override
  Future<Snapshot> load() async {
    final result = await Future.wait([
      api.request('GET', 'profile/'),
      api.request('GET', 'contacts/'),
      api.request('GET', 'journeys/'),
      api.request('GET', 'alerts/'),
      api.request('GET', 'capabilities/'),
    ]);
    return Snapshot(
        Profile(name: result[0]['name'], email: result[0]['email']),
        (result[1] as List)
            .map((v) => Contact(
                id: v['id'],
                name: v['name'],
                phone: v['phone'],
                email: v['email'],
                relationship: v['relationship']))
            .toList(),
        (result[3] as List).map((v) => _alert(v)).toList(),
        (result[2] as List)
            .map((v) => Journey(
                id: v['id'],
                destination: v['destination'],
                deadline: DateTime.parse(v['deadline']),
                state: v['state']))
            .toList(),
        result[4]['sms'] == true,
        result[4]['email'] == true);
  }

  @override
  Future<void> saveContact(Contact contact) async => api.request(
          contact.id == null ? 'POST' : 'PATCH',
          contact.id == null ? 'contacts/' : 'contacts/${contact.id}/', {
        'name': contact.name,
        'phone': contact.phone,
        'email': contact.email,
        'relationship': contact.relationship
      });
  @override
  Future<void> deleteContact(int id) async =>
      api.request('DELETE', 'contacts/$id/');
  @override
  Future<void> saveProfile(String name) async =>
      api.request('PATCH', 'profile/', {'name': name});
  @override
  Future<SafetyAlert> activateSos(GeoPoint? location) async {
    _pendingId ??= await storage.read(key: _pendingKey) ?? const Uuid().v4();
    await storage.write(key: _pendingKey, value: _pendingId);
    final result = await api.request('POST', 'alerts/', {
      'request_id': _pendingId,
      if (location != null) ...{
        'latitude': location.latitude,
        'longitude': location.longitude,
        'location_at': location.timestamp.toUtc().toIso8601String(),
        'location_accuracy': location.accuracy,
      },
    });
    await storage.delete(key: _pendingKey);
    _pendingId = null;
    return _alert(result);
  }

  @override
  Future<void> resolveAlert(int id) async =>
      api.request('POST', 'alerts/$id/resolve/');
  @override
  Future<void> retryAlert(int id) async =>
      api.request('POST', 'alerts/$id/retry/');
  @override
  Future<void> startJourney(String destination, DateTime deadline) async =>
      api.request('POST', 'journeys/', {
        'destination': destination,
        'deadline': deadline.toUtc().toIso8601String()
      });
  @override
  Future<void> finishJourney(int id, {required bool arrived}) async =>
      api.request('POST', 'journeys/$id/${arrived ? 'arrive' : 'cancel'}/');
  SafetyAlert _alert(Map<String, dynamic> value) => SafetyAlert(
        id: value['id'],
        createdAt: DateTime.parse(value['created_at']),
        reason: value['reason'],
        resolvedAt: value['resolved_at'] == null
            ? null
            : DateTime.parse(value['resolved_at']),
        location: value['latitude'] == null
            ? null
            : GeoPoint(
                (value['latitude'] as num).toDouble(),
                (value['longitude'] as num).toDouble(),
                (value['location_accuracy'] as num?)?.toDouble() ?? 0,
                DateTime.parse(value['location_at'] ?? value['created_at'])),
        deliveries: (value['deliveries'] as List)
            .map((v) => RecipientDelivery(v['name'], v['status'], v['channel']))
            .toList(),
      );
}
