import 'entities.dart';
import 'repositories.dart';

class SaveContact {
  const SaveContact(this.repository);
  final SafetyRepository repository;
  Future<void> call(Contact contact) {
    if (contact.name.trim().isEmpty) {
      throw const QorgoException('Укажите имя контакта.');
    }
    final phone = normalizeContactPhone(contact.phone);
    if (!RegExp(r'^\+[1-9]\d{7,14}$').hasMatch(phone)) {
      throw const QorgoException('Номер должен начинаться с + и кода страны.');
    }
    return repository.saveContact(Contact(
        id: contact.id,
        name: contact.name.trim(),
        phone: phone,
        email: contact.email.trim(),
        relationship: contact.relationship.trim(),
        linkRegistered: contact.linkRegistered));
  }
}

class StartJourney {
  const StartJourney(this.repository);
  final SafetyRepository repository;
  Future<void> call(String destination, Duration duration, DateTime now) {
    if (destination.trim().isEmpty) {
      throw const QorgoException('Укажите пункт назначения.');
    }
    if (duration <= Duration.zero || duration > const Duration(hours: 24)) {
      throw const QorgoException('Укажите время от 1 минуты до 24 часов.');
    }
    return repository.startJourney(destination.trim(), now.add(duration));
  }
}

class ActivateSos {
  const ActivateSos(this.repository);
  final SafetyRepository repository;
  Future<SafetyAlert> call(GeoPoint? point) => repository.activateSos(point);
}

String normalizeContactPhone(String value) {
  var phone = value.trim().replaceAll(RegExp(r'[\s()\-]'), '');
  if (phone.startsWith('00')) phone = '+${phone.substring(2)}';
  if (RegExp(r'^0[57]\d{8}$').hasMatch(phone)) {
    phone = '+996${phone.substring(1)}';
  }
  if (RegExp(r'^[57]\d{8}$').hasMatch(phone)) phone = '+996$phone';
  if (RegExp(r'^996\d{9}$').hasMatch(phone)) phone = '+$phone';
  if (!RegExp(r'^\+[1-9]\d{7,14}$').hasMatch(phone)) {
    throw const QorgoException(
        'Укажите международный номер, например +996700123456.');
  }
  return phone;
}

class FindRegisteredContact {
  const FindRegisteredContact(this.repository);
  final SafetyRepository repository;
  Future<RegisteredContactMatch?> call(String phone) =>
      repository.findRegisteredContact(normalizeContactPhone(phone));
}
