import '../../core/state/view_model.dart';
import '../../domain/entities.dart';
import '../../domain/repositories.dart';
import '../../domain/use_cases.dart';

class ContactLookupViewModel extends ViewModel {
  ContactLookupViewModel(this._repository, this._device);
  final SafetyRepository _repository;
  final DeviceGateway _device;
  RegisteredContactMatch? match;
  bool busy = false, searched = false;
  String? error;
  int _revision = 0;

  void clear() {
    _revision++;
    match = null;
    searched = false;
    error = null;
    notifyState();
  }

  Future<void> search(String phone) async {
    if (busy || disposed) return;
    final revision = ++_revision;
    busy = true;
    error = null;
    match = null;
    searched = false;
    notifyState();
    try {
      final found = await FindRegisteredContact(_repository)(phone);
      if (!disposed && revision == _revision) {
        match = found;
        searched = true;
      }
    } catch (e) {
      if (!disposed && revision == _revision) {
        error = e is QorgoException
            ? e.message
            : 'Не удалось проверить номер. Попробуйте ещё раз.';
      }
    } finally {
      busy = false;
      notifyState();
    }
  }

  Future<DeviceContact?> pick() async {
    if (busy || disposed) return null;
    busy = true;
    error = null;
    notifyState();
    DeviceContact? selected;
    try {
      selected = await _device.pickContact();
      if (selected != null) {
        selected =
            DeviceContact(selected.name, normalizeContactPhone(selected.phone));
      }
    } catch (e) {
      error = e is QorgoException ? e.message : 'Не удалось открыть контакты.';
    } finally {
      busy = false;
      notifyState();
    }
    if (disposed) return null;
    if (selected != null) await search(selected.phone);
    return selected;
  }
}
