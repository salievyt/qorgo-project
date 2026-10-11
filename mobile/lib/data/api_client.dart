import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../domain/entities.dart';

class ApiClient {
  ApiClient(this.baseUrl, {http.Client? client})
      : client = client ?? http.Client() {
    if (kReleaseMode && Uri.parse(baseUrl).scheme != 'https') {
      throw const QorgoException('Для сервера требуется HTTPS.');
    }
  }
  final String baseUrl;
  final http.Client client;
  String? token;
  Future<dynamic> request(String method, String path,
      [Map<String, dynamic>? body]) async {
    try {
      final request = http.Request(method, Uri.parse('$baseUrl/$path'));
      request.headers['Content-Type'] = 'application/json';
      if (token != null) request.headers['Authorization'] = 'Token $token';
      if (body != null) request.body = jsonEncode(body);
      final response = await http.Response.fromStream(
              await client.send(request).timeout(const Duration(seconds: 15)))
          .timeout(const Duration(seconds: 15));
      dynamic data;
      if (response.body.isNotEmpty) {
        try {
          data = jsonDecode(utf8.decode(response.bodyBytes));
        } catch (_) {
          throw const QorgoException('Сервер вернул некорректный ответ.');
        }
      }
      if (response.statusCode == 401) {
        throw const QorgoException('Войдите в аккаунт повторно.',
            unauthorized: true);
      }
      if (response.statusCode >= 400) {
        final message = data is Map
            ? (data['detail'] ?? data.values.first).toString()
            : 'Ошибка сервера';
        throw QorgoException(message);
      }
      return data;
    } on TimeoutException {
      throw const QorgoException(
          'Сервер не ответил вовремя. Проверьте связь и повторите.');
    } on http.ClientException {
      throw const QorgoException(
          'Нет соединения с сервером. Проверьте интернет.');
    }
  }
}
