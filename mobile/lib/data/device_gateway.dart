import 'package:geolocator/geolocator.dart';
import 'package:flutter/services.dart';
import 'package:flutter_native_contact_picker/flutter_native_contact_picker.dart'
    as native_contacts;
import 'package:url_launcher/url_launcher.dart';
import '../domain/entities.dart';
import '../domain/repositories.dart';

class NativeDeviceGateway implements DeviceGateway {
  @override
  Future<DeviceContact?> pickContact() async {
    try {
      final picked = await native_contacts.FlutterNativeContactPicker()
          .selectPhoneNumber();
      if (picked == null) return null;
      final phone = picked.selectedPhoneNumber ??
          (picked.phoneNumbers?.length == 1
              ? picked.phoneNumbers!.single
              : null);
      if (phone == null || phone.trim().isEmpty) {
        throw const QorgoException('Выберите контакт с номером телефона.');
      }
      return DeviceContact(picked.fullName ?? '', phone);
    } on PlatformException {
      throw const QorgoException(
          'Не удалось открыть контакты. Можно ввести номер вручную.');
    }
  }

  @override
  Future<GeoPoint> locate() async {
    if (!await Geolocator.isLocationServiceEnabled()) {
      throw const QorgoException('Включите геолокацию в настройках телефона.');
    }
    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    if (permission == LocationPermission.denied ||
        permission == LocationPermission.deniedForever) {
      throw const QorgoException(
          'Доступ к геолокации не разрешён. SOS можно отправить без координат.');
    }
    final p = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
            accuracy: LocationAccuracy.high, timeLimit: Duration(seconds: 10)));
    return GeoPoint(p.latitude, p.longitude, p.accuracy, p.timestamp);
  }

  @override
  Stream<GeoPoint> trackLocation() async* {
    if (!await Geolocator.isLocationServiceEnabled()) {
      throw const QorgoException('Включите геолокацию в настройках телефона.');
    }
    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    if (permission == LocationPermission.denied ||
        permission == LocationPermission.deniedForever) {
      throw const QorgoException(
          'Для непрерывной защиты нужен доступ к геолокации.');
    }
    const settings =
        LocationSettings(accuracy: LocationAccuracy.high, distanceFilter: 5);
    await for (final p
        in Geolocator.getPositionStream(locationSettings: settings)) {
      yield GeoPoint(p.latitude, p.longitude, p.accuracy, p.timestamp);
    }
  }

  Future<void> _open(Uri uri) async {
    if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
      throw const QorgoException(
          'Телефон не поддерживает это действие. На симуляторе звонки и SMS могут быть недоступны.');
    }
  }

  @override
  Future<void> openMap(GeoPoint point) => _open(Uri.parse(point.mapUrl));
  @override
  Future<void> call(String phone) => _open(Uri(scheme: 'tel', path: phone));
  @override
  Future<void> composeSms(Contact contact, String message) => _open(Uri(
      scheme: 'sms',
      path: contact.phone,
      query: 'body=${Uri.encodeComponent(message)}'));
}
