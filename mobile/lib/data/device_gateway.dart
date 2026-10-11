import 'package:geolocator/geolocator.dart';
import 'package:url_launcher/url_launcher.dart';
import '../domain/entities.dart';
import '../domain/repositories.dart';

class NativeDeviceGateway implements DeviceGateway {
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
