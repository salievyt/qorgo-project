import 'dart:async';
import 'package:flutter/foundation.dart';
import '../domain/entities.dart';
import '../domain/repositories.dart';
import '../domain/use_cases.dart';

class AppController extends ChangeNotifier {
  AppController(this.repository, this.device);
  final SafetyRepository repository;
  final DeviceGateway device;
  Snapshot? snapshot;
  GeoPoint? location;
  bool initialized = false, signedIn = false, busy = false;
  String? error;
  DateTime? syncedAt;
  Timer? _poller;
  bool _refreshing = false;
  bool _disposed = false;
  int _revision = 0;
  void _notify() {
    if (!_disposed) notifyListeners();
  }

  SafetyAlert? get activeAlert =>
      snapshot?.alerts.where((a) => a.resolvedAt == null).firstOrNull;
  Journey? get activeJourney =>
      snapshot?.journeys.where((j) => j.active).firstOrNull;

  Future<void> initialize() async {
    try {
      signedIn = await repository.restoreSession();
      if (signedIn) await refresh();
    } catch (e) {
      _recordError(e);
    }
    initialized = true;
    if (_disposed) return;
    _poller ??= Timer.periodic(
        const Duration(seconds: 10), (_) => refresh(silent: true));
    _notify();
  }

  void _recordError(Object e) {
    error = e is QorgoException
        ? e.message
        : 'Не удалось выполнить действие. Повторите попытку.';
    if (e is QorgoException && e.unauthorized) {
      signedIn = false;
      snapshot = null;
    }
  }

  Future<void> refresh({bool silent = false}) async {
    if (_disposed || !signedIn || busy || _refreshing) return;
    _refreshing = true;
    final revision = _revision;
    try {
      final loaded = await repository.load();
      if (_disposed || revision != _revision) return;
      snapshot = loaded;
      syncedAt = DateTime.now();
      error = null;
    } catch (e) {
      _recordError(e);
    } finally {
      _refreshing = false;
      _notify();
    }
  }

  Future<bool> perform(Future<void> Function() action,
      {bool reload = true}) async {
    if (_disposed || busy) return false;
    _revision++;
    busy = true;
    error = null;
    _notify();
    try {
      await action();
      if (reload && signedIn) {
        snapshot = await repository.load();
        syncedAt = DateTime.now();
      }
      return true;
    } catch (e) {
      _recordError(e);
      return false;
    } finally {
      busy = false;
      _notify();
    }
  }

  Future<bool> authenticate(String email, String password, {String? name}) =>
      perform(() async {
        await repository.signIn(email, password, name: name);
        signedIn = true;
      });
  Future<void> logout() async {
    await perform(() async {
      try {
        await repository.signOut();
      } finally {
        signedIn = false;
        snapshot = null;
        location = null;
      }
    }, reload: false);
  }

  Future<bool> saveContact(Contact contact) =>
      perform(() => SaveContact(repository)(contact));
  Future<bool> deleteContact(Contact contact) =>
      perform(() => repository.deleteContact(contact.id!));
  Future<bool> saveProfile(String name) =>
      perform(() => repository.saveProfile(name.trim()));
  Future<bool> updateLocation() => perform(() async {
        location = await device.locate();
      }, reload: false);
  Future<bool> activateSos() => perform(() async {
        // A denied or slow location request must not prevent sending the alert.
        GeoPoint? current;
        try {
          current = await device.locate();
          location = current;
        } catch (_) {
          current = null;
        }
        await ActivateSos(repository)(current, snapshot?.contacts ?? []);
      });
  Future<bool> resolveAlert(int id) =>
      perform(() => repository.resolveAlert(id));
  Future<bool> retryAlert(int id) => perform(() => repository.retryAlert(id));
  Future<bool> startJourney(String destination, int minutes) =>
      perform(() => StartJourney(repository)(
          destination, Duration(minutes: minutes), DateTime.now()));
  Future<bool> finishJourney(Journey journey, bool arrived) =>
      perform(() => repository.finishJourney(journey.id, arrived: arrived));
  Future<bool> call(String phone) =>
      perform(() => device.call(phone), reload: false);
  Future<bool> openMap() => perform(() async {
        final point = location ?? activeAlert?.location;
        if (point == null) {
          throw const QorgoException('Сначала определите местоположение.');
        }
        await device.openMap(point);
      }, reload: false);
  Future<bool> composeSms(Contact contact) => perform(() async {
        final point = activeAlert?.location ?? location;
        final name = snapshot?.profile.name ?? '';
        await device.composeSms(contact,
            'QORGO SOS: $name просит о помощи. ${point?.mapUrl ?? 'Геопозиция недоступна.'}');
      }, reload: false);
  @override
  void dispose() {
    _disposed = true;
    _poller?.cancel();
    super.dispose();
  }
}
