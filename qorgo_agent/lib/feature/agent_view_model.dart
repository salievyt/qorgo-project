import 'dart:async';

import 'package:flutter/foundation.dart';

import '../data/agent_repository.dart';
import '../domain/incident.dart';

class AgentViewModel extends ChangeNotifier {
  AgentViewModel(this.repository);
  final IncidentRepository repository;
  List<Incident> incidents = const [];
  bool ready = false, signedIn = false, busy = false;
  String? error;
  Timer? _poller;
  Future<void> initialize() async {
    signedIn = await repository.restore();
    ready = true;
    if (signedIn) await refresh();
    notifyListeners();
  }

  Future<bool> login(String phone, String password) => _run(() async {
    await repository.login(phone, password);
    signedIn = true;
    await refresh();
  });
  Future<void> logout() async {
    _poller?.cancel();
    await repository.logout();
    signedIn = false;
    incidents = const [];
    notifyListeners();
  }

  Future<void> refresh() async {
    if (!signedIn || busy) return;
    try {
      incidents = await repository.load();
      error = null;
      _poller ??= Timer.periodic(const Duration(seconds: 8), (_) => refresh());
    } catch (e) {
      error = e is AgentException ? e.message : 'Не удалось обновить очередь.';
    }
    notifyListeners();
  }

  Future<bool> take(String id) => _run(() async {
    await repository.take(id);
    await refresh();
  });
  Future<bool> close(String id, String status, String note) => _run(() async {
    await repository.close(id, status, note);
    await refresh();
  });
  Future<bool> _run(Future<void> Function() action) async {
    if (busy) return false;
    busy = true;
    error = null;
    notifyListeners();
    try {
      await action();
      return true;
    } catch (e) {
      error = e is AgentException
          ? e.message
          : 'Не удалось выполнить действие.';
      return false;
    } finally {
      busy = false;
      notifyListeners();
    }
  }

  @override
  void dispose() {
    _poller?.cancel();
    super.dispose();
  }
}
