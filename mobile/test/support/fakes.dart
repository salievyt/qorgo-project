import 'package:qorgo/domain/entities.dart';
import 'package:qorgo/domain/repositories.dart';

class FakeRepository implements SafetyRepository {
  bool authenticated = true;
  Profile profile = const Profile(name: 'Тест', email: 'test@example.invalid');
  final contacts = <Contact>[];
  @override
  Future<bool> restoreSession() async => authenticated;
  @override
  Future<Snapshot> load() async =>
      Snapshot(profile, List.of(contacts), [], [], false, false);
  @override
  Future<void> saveContact(Contact contact) async {
    contacts.add(Contact(
        id: contacts.length + 1,
        name: contact.name,
        phone: contact.phone,
        email: contact.email));
  }

  @override
  Future<void> signIn(String email, String password, {String? name}) async {
    authenticated = true;
    profile = Profile(name: name ?? '', email: email);
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class FakeDevice implements DeviceGateway {
  @override
  Future<GeoPoint> locate() async =>
      throw const QorgoException('Геопозиция недоступна');
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}
