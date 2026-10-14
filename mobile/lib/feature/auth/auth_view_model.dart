import '../../domain/repositories.dart';

/// Authentication state is independent of Flutter views and transport details.
class AuthViewModel {
  AuthViewModel(this._repository);
  final SafetyRepository _repository;
  bool signedIn = false;

  Future<void> restore() async {
    signedIn = await _repository.restoreSession();
  }

  Future<void> authenticate(String email, String password,
      {String? name}) async {
    await _repository.signIn(email, password, name: name);
    signedIn = true;
  }

  Future<void> logout() async {
    try {
      await _repository.signOut();
    } finally {
      signedIn = false;
    }
  }
}
