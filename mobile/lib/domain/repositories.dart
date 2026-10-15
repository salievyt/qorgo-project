import 'entities.dart';

abstract interface class SafetyRepository {
  Future<RegisteredContactMatch?> findRegisteredContact(String phone);
  Future<void> acknowledge(int deliveryId);
  Future<bool> restoreSession();
  Future<void> signIn(String email, String password, {String? name});
  Future<void> signOut();
  Future<Snapshot> load();
  Future<void> saveContact(Contact contact);
  Future<void> deleteContact(int id);
  Future<void> saveProfile(String name, {String? phone});
  Future<SafetyAlert> activateSos(GeoPoint? location);
  Future<void> resolveAlert(int id);
  Future<void> retryAlert(int id);
  Future<void> startJourney(String destination, DateTime deadline);
  Future<void> finishJourney(int id, {required bool arrived});
  Future<void> recordLocation(GeoPoint point, {required bool background});
  Future<bool> operatorLocationSharingEnabled();
  Future<void> setOperatorLocationSharing(bool enabled);
}

abstract interface class DeviceGateway {
  Future<DeviceContact?> pickContact();
  Future<GeoPoint> locate();
  Stream<GeoPoint> trackLocation();
  Future<void> openMap(GeoPoint point);
  Future<void> call(String phone);
  Future<void> composeSms(Contact contact, String message);
}
