import 'entities.dart';
import 'repositories.dart';

class SaveContact {
  const SaveContact(this.repository);
  final SafetyRepository repository;
  Future<void> call(Contact contact) {
    if (contact.name.trim().isEmpty) {
      throw const QorgoException('Укажите имя контакта.');
    }
    final phone = contact.phone.replaceAll(RegExp(r'[\s()\-]'), '');
    if (!RegExp(r'^\+[1-9]\d{7,14}$').hasMatch(phone)) {
      throw const QorgoException('Номер должен начинаться с + и кода страны.');
    }
    return repository.saveContact(Contact(
        id: contact.id,
        name: contact.name.trim(),
        phone: phone,
        email: contact.email.trim(),
        relationship: contact.relationship.trim()));
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
  Future<SafetyAlert> call(GeoPoint? point, List<Contact> contacts) {
    if (contacts.isEmpty) {
      throw const QorgoException('Сначала добавьте доверенный контакт.');
    }
    return repository.activateSos(point);
  }
}
