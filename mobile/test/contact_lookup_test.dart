import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:qorgo/domain/entities.dart';
import 'package:qorgo/domain/use_cases.dart';
import 'package:qorgo/feature/app/app_view.dart';
import 'package:qorgo/feature/app/app_view_model.dart';
import 'support/fakes.dart';

class MatchedRepository extends FakeRepository {
  String? searchedPhone;
  @override
  Future<RegisteredContactMatch?> findRegisteredContact(String phone) async {
    searchedPhone = phone;
    return const RegisteredContactMatch(
        name: 'Friend Account', phone: '+996700123456', alreadyAdded: false);
  }
}

class SelectedContactDevice extends FakeDevice {
  @override
  Future<DeviceContact?> pickContact() async =>
      const DeviceContact('Мой лучший друг', '0700 123-456');
}

void main() {
  test('Phone numbers from the address book normalize to international format',
      () {
    for (final value in [
      '0700 123-456',
      '700123456',
      '996700123456',
      '+996 (700) 123-456',
      '00996700123456'
    ]) {
      expect(normalizeContactPhone(value), '+996700123456');
    }
    expect(() => normalizeContactPhone('123'), throwsA(isA<QorgoException>()));
  });
  testWidgets('Selected registered friend is saved without entering email',
      (tester) async {
    final repository = MatchedRepository();
    final vm = AppViewModel(repository, SelectedContactDevice());
    await vm.initialize();
    await tester
        .pumpWidget(QorgoApp(controller: vm, splashDuration: Duration.zero));
    await tester.tap(find.text('Близкие'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Добавить близкого'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Выбрать из контактов'));
    await tester.pumpAndSettle();
    expect(repository.searchedPhone, '+996700123456');
    expect(find.text('Friend Account'), findsOneWidget);
    expect(find.text('Есть в QORGO — можно сразу добавить'), findsOneWidget);
    await tester.ensureVisible(find.text('Добавить в близкие'));
    await tester.tap(find.text('Добавить в близкие'));
    await tester.pumpAndSettle();
    expect(repository.contacts.single.name, 'Мой лучший друг');
    expect(repository.contacts.single.email, isEmpty);
    expect(repository.contacts.single.linkRegistered, true);
    expect(find.text('В QORGO'), findsOneWidget);
    await tester.pumpWidget(const SizedBox());
    vm.dispose();
  });
}
