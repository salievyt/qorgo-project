import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

import '../domain/incident.dart';

class AgentException implements Exception {
  const AgentException(this.message);
  final String message;
}

class HttpIncidentRepository implements IncidentRepository {
  HttpIncidentRepository({http.Client? client})
    : _client = client ?? http.Client();
  static const _url = String.fromEnvironment(
    'QORGO_API_URL',
    defaultValue: 'https://api.qorgo.services/api/v1',
  );
  static const _key = 'qorgo.agent.access';
  final http.Client _client;
  final _storage = const FlutterSecureStorage();
  String? _token;
  Future<dynamic> _request(
    String method,
    String path, [
    Map<String, dynamic>? body,
  ]) async {
    final response = await _client
        .send(
          http.Request(method, Uri.parse('$_url/$path'))
            ..headers.addAll({
              'Content-Type': 'application/json',
              if (_token != null) 'Authorization': 'Bearer $_token',
            })
            ..body = body == null ? '' : jsonEncode(body),
        )
        .then(http.Response.fromStream);
    dynamic data = response.body.isEmpty
        ? null
        : jsonDecode(utf8.decode(response.bodyBytes));
    if (response.statusCode >= 400) {
      throw AgentException(
        data is Map
            ? (data['detail'] ?? data['error'] ?? 'Ошибка доступа').toString()
            : 'Ошибка сервера',
      );
    }
    return data;
  }

  @override
  Future<bool> restore() async {
    _token = await _storage.read(key: _key);
    return _token != null;
  }

  @override
  Future<void> login(String phone, String password) async {
    final data = await _request('POST', 'auth/login/', {
      'phone_number': phone.trim(),
      'password': password,
    });
    _token = data['access'];
    await _storage.write(key: _key, value: _token);
  }

  @override
  Future<void> logout() async {
    await _storage.delete(key: _key);
    _token = null;
  }

  Incident _incident(Map<String, dynamic> v) {
    final user = v['user'] as Map<String, dynamic>? ?? {};
    final first = user['first_name']?.toString() ?? '';
    final last = user['last_name']?.toString() ?? '';
    return Incident(
      id: v['id'].toString(),
      name: ('$first $last').trim().isEmpty
          ? 'Пользователь QORGO'
          : ('$first $last').trim(),
      phone: user['phone_number']?.toString() ?? '',
      latitude: (v['latitude'] as num).toDouble(),
      longitude: (v['longitude'] as num).toDouble(),
      address: v['address']?.toString() ?? '',
      battery: (v['battery_level'] as num?)?.toDouble() ?? 0,
      trigger: v['trigger_method']?.toString() ?? 'sos_button',
      assignedTo: v['assigned_operator_name']?.toString() ?? '',
      startedAt: DateTime.parse(v['started_at']),
    );
  }

  @override
  Future<List<Incident>> load() async {
    final data = await _request('GET', 'operator/incidents/');
    return ((data['results'] ?? data) as List)
        .map((v) => _incident(v))
        .toList();
  }

  @override
  Future<Incident> take(String id) async =>
      _incident(await _request('POST', 'operator/incidents/$id/take/'));
  @override
  Future<void> close(String id, String status, String note) async => _request(
    'POST',
    'operator/incidents/$id/close/',
    {'status': status, 'note': note},
  );
}
