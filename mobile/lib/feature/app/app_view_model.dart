import '../../domain/repositories.dart';
import '../../data/protection_consent_store.dart';
import '../contacts/contact_lookup_view_model.dart';
import '../auth/auth_view_model.dart';
import '../safety/safety_view_model.dart';

/// Coordinates session lifecycle and the safety feature without knowing HTTP.
class AppViewModel extends SafetyViewModel {
  // Explicit arguments allow the session view model to share the repository.
  // ignore: use_super_parameters
  AppViewModel(SafetyRepository repository, DeviceGateway device,
      {ProtectionConsentStore? protectionConsent})
      : auth = AuthViewModel(repository),
        _protectionConsent = protectionConsent ?? ProtectionConsentStore(),
        super(repository, device);
  final AuthViewModel auth;
  final ProtectionConsentStore _protectionConsent;
  Future<bool> shouldExplainProtection() => _protectionConsent.shouldExplain();
  Future<void> markProtectionExplained() => _protectionConsent.markExplained();
  ContactLookupViewModel createContactLookup() =>
      ContactLookupViewModel(repository, device);

  Future<void> initialize() async {
    await perform(() async {
      await auth.restore();
      signedIn = auth.signedIn;
      if (signedIn) {
        try {
          continuousProtection = await repository.operatorLocationSharingEnabled();
        } catch (_) {
          continuousProtection = false;
        }
      }
    });
    initialized = true;
    startPolling();
    notifyState();
  }

  Future<bool> authenticate(String email, String password, {String? name}) =>
      perform(() async {
        await auth.authenticate(email, password, name: name);
        signedIn = auth.signedIn;
        continuousProtection = await repository.operatorLocationSharingEnabled();
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
