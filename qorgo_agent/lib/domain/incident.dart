class Incident {
  const Incident({
    required this.id,
    required this.name,
    required this.phone,
    required this.latitude,
    required this.longitude,
    required this.startedAt,
    required this.trigger,
    required this.assignedTo,
    this.address = '',
    this.battery = 0,
  });
  final String id, name, phone, trigger, assignedTo, address;
  final double latitude, longitude, battery;
  final DateTime startedAt;
}

abstract interface class IncidentRepository {
  Future<bool> restore();
  Future<void> login(String phone, String password);
  Future<void> logout();
  Future<List<Incident>> load();
  Future<Incident> take(String id);
  Future<void> close(String id, String status, String note);
}
