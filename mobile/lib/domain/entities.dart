class Contact {
  const Contact(
      {this.id,
      required this.name,
      required this.phone,
      this.email = '',
      this.relationship = ''});
  final int? id;
  final String name, phone, email, relationship;
}

class Profile {
  const Profile({required this.name, required this.email});
  final String name, email;
}

class GeoPoint {
  const GeoPoint(this.latitude, this.longitude, this.accuracy, this.timestamp);
  final double latitude, longitude, accuracy;
  final DateTime timestamp;
  String get mapUrl => 'https://www.google.com/maps?q=$latitude,$longitude';
}

class RecipientDelivery {
  const RecipientDelivery(this.name, this.status, this.channel);
  final String name, status, channel;
  String get label => switch (status) {
        'accepted' => 'Принято сервисом ${channel == 'sms' ? 'SMS' : 'email'}',
        'unconfigured' => 'Сервис отправки не подключён',
        'unknown' => 'Результат отправки неизвестен',
        'sending' => 'Отправляется',
        'cancelled' => 'Отменено до отправки',
        _ => 'В очереди',
      };
}

class SafetyAlert {
  const SafetyAlert(
      {required this.id,
      required this.createdAt,
      required this.reason,
      required this.deliveries,
      this.location,
      this.resolvedAt});
  final int id;
  final DateTime createdAt;
  final String reason;
  final List<RecipientDelivery> deliveries;
  final GeoPoint? location;
  final DateTime? resolvedAt;
  String get title =>
      reason == 'timer' ? 'Время прибытия истекло' : 'Сигнал SOS';
  String get status => resolvedAt != null
      ? 'Тревога завершена'
      : deliveries.isEmpty
          ? 'Нет получателей'
          : deliveries.every((d) => d.status == 'accepted')
              ? 'Принято сервисом отправки'
              : deliveries.any((d) => d.status == 'unknown')
                  ? 'Требует проверки отправки'
                  : deliveries.any((d) => d.status == 'unconfigured')
                      ? 'Ожидает подключения отправки'
                      : 'Обрабатывается';
}

class Journey {
  const Journey(
      {required this.id,
      required this.destination,
      required this.deadline,
      required this.state});
  final int id;
  final String destination, state;
  final DateTime deadline;
  bool get active => state == 'active';
  String get label => switch (state) {
        'arrived' => 'Прибытие подтверждено',
        'cancelled' => 'Отменён',
        'expired' => 'Время истекло — создан SOS',
        _ => 'Ожидаем прибытия',
      };
}

class Snapshot {
  const Snapshot(this.profile, this.contacts, this.alerts, this.journeys,
      this.smsReady, this.emailReady);
  final Profile profile;
  final List<Contact> contacts;
  final List<SafetyAlert> alerts;
  final List<Journey> journeys;
  final bool smsReady, emailReady;
  bool get deliveryReady => smsReady || emailReady;
}

class QorgoException implements Exception {
  const QorgoException(this.message, {this.unauthorized = false});
  final String message;
  final bool unauthorized;
  @override
  String toString() => message;
}
