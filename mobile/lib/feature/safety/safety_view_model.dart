import 'dart:async';
import '../../core/state/view_model.dart';
import '../../domain/entities.dart';
import '../../domain/repositories.dart';
import '../../domain/use_cases.dart';

class SafetyViewModel extends ViewModel {
  SafetyViewModel(this.repository, this.device);
  final SafetyRepository repository;
  final DeviceGateway device;
  Snapshot? snapshot;
  GeoPoint? location;
  bool initialized = false, signedIn = false, busy = false;
  String? error;
  DateTime? syncedAt;
  Timer? _poller;
  StreamSubscription<GeoPoint>? _tracking;
  bool continuousProtection = false;
  DateTime? lastLocationSent;
  bool _refreshing = false;
  int _revision = 0;
  SafetyAlert? get activeAlert =>
      snapshot?.alerts.where((a) => a.resolvedAt == null).firstOrNull;
  Journey? get activeJourney =>
      snapshot?.journeys.where((j) => j.active).firstOrNull;

  void startPolling() {
    if (disposed) return;
    _poller ??= Timer.periodic(
        const Duration(seconds: 5), (_) => refresh(silent: true));
  }

  Future<void> startContinuousProtection() async {
    if (!signedIn || !continuousProtection || _tracking != null) return;
    try {
      _tracking = device.trackLocation().listen((point) async {
        final moving = point.accuracy <= 100;
        final interval = activeAlert != null
            ? const Duration(seconds: 5)
            : moving
                ? const Duration(seconds: 10)
                : const Duration(minutes: 1);
        if (lastLocationSent == null ||
            DateTime.now().difference(lastLocationSent!) >= interval) {
          await repository.recordLocation(point, background: true);
          location = point;
          lastLocationSent = DateTime.now();
          notifyState();
        }
      }, onError: _recordError);
    } catch (e) {
      _recordError(e);
      notifyState();
    }
  }

  Future<void> setContinuousProtection(bool enabled) async {
    if (!enabled) {
      continuousProtection = false;
      await _tracking?.cancel();
      _tracking = null;
      notifyState();
    }
    try {
      await repository.setOperatorLocationSharing(enabled);
      continuousProtection = enabled;
      if (enabled) {
        lastLocationSent = null;
        await startContinuousProtection();
      }
    } catch (e) {
      _recordError(e);
    }
    notifyState();
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
    if (disposed || !signedIn || busy || _refreshing) return;
    _refreshing = true;
    final revision = _revision;
    try {
      final loaded = await repository.load();
      if (disposed || revision != _revision) return;
      snapshot = loaded;
      syncedAt = DateTime.now();
      error = null;
    } catch (e) {
      _recordError(e);
    } finally {
      _refreshing = false;
      notifyState();
    }
  }

  Future<bool> perform(Future<void> Function() action,
      {bool reload = true}) async {
    if (disposed || busy) return false;
    _revision++;
    busy = true;
    error = null;
    notifyState();
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
      notifyState();
    }
  }

  Future<bool> acknowledge(int deliveryId) =>
      perform(() => repository.acknowledge(deliveryId));
  Future<bool> openAlertMap(GeoPoint point) =>
      perform(() => device.openMap(point), reload: false);

  Future<bool> saveContact(Contact contact) =>
      perform(() => SaveContact(repository)(contact));
  Future<bool> deleteContact(Contact contact) =>
      perform(() => repository.deleteContact(contact.id!));
  Future<bool> saveProfile(String name, {String? phone}) =>
      perform(() => repository.saveProfile(name.trim(), phone: phone));
  Future<bool> updateLocation() => perform(() async {
        location = await device.locate();
      }, reload: false);
  Future<bool> activateSos() => perform(() async {
        // A denied or slow location request must not prevent sending the alert.
        GeoPoint? current;
        try {
          current = await device.locate();
          location = current;
          try {
            await repository.recordLocation(current, background: false);
          } catch (_) {
            // The SOS request itself must still be sent if a location sync fails.
          }
        } catch (_) {
          current = null;
        }
        await ActivateSos(repository)(current);
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
    _poller?.cancel();
    _tracking?.cancel();
    super.dispose();
  }
}
