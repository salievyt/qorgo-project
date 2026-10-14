abstract final class Environment {
  static const mapTileUrl = String.fromEnvironment('QORGO_MAP_TILE_URL',
      defaultValue: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png');
  static const mapAttribution = String.fromEnvironment('QORGO_MAP_ATTRIBUTION',
      defaultValue: '© OpenStreetMap contributors');
  static const apiUrl = String.fromEnvironment('QORGO_API_URL',
      defaultValue: 'https://api.qorgo.services/api');
}
