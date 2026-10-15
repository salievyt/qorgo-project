import '../../domain/repositories.dart';
import '../contacts/contact_lookup_view_model.dart';
import '../auth/auth_view_model.dart';
import '../safety/safety_view_model.dart';

/// Coordinates session lifecycle and the safety feature without knowing HTTP.
class AppViewModel extends SafetyViewModel {
  // Explicit arguments allow the session view model to share the repository.
  // ignore: use_super_parameters
  AppViewModel(SafetyRepository repository, DeviceGateway device)
      : auth = AuthViewModel(repository),
        super(repository, device);
  final AuthViewModel auth;
  ContactLookupViewModel createContactLookup() =>
      ContactLookupViewModel(repository, device);

  Future<void> initialize() async {
    await perform(() async {
      await auth.restore();
      signedIn = auth.signedIn;
    });
    initialized = true;
    startPolling();
    notifyState();
  }

  Future<bool> authenticate(String email, String password, {String? name}) =>
      perform(() async {
        await auth.authenticate(email, password, name: name);
        signedIn = auth.signedIn;
      });

  Future<void> logout() async {
    await perform(() async {
      try {
        await auth.logout();
      } finally {
        signedIn = false;
        snapshot = null;
        location = null;
      }
    }, reload: false);
  }
}
