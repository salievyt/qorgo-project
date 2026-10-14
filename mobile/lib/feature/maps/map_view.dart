import '../../core/design/qorgo_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../core/config/environment.dart';
import '../../domain/entities.dart';

class OpenStreetMapView extends StatefulWidget {
  const OpenStreetMapView({
    super.key,
    required this.point,
    required this.title,
    this.tileProvider,
  });
  final GeoPoint point;
  final String title;
  // Allows an alternate tile provider for testing or deployment.
  final TileProvider? tileProvider;

  @override
  State<OpenStreetMapView> createState() => _OpenStreetMapViewState();
}

class _OpenStreetMapViewState extends State<OpenStreetMapView> {
  final _controller = MapController();
  bool _tileError = false;
  LatLng get _position => LatLng(widget.point.latitude, widget.point.longitude);

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _open(String url) async {
    var opened = false;
    try {
      opened =
          await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
    } catch (_) {
      // Keep the map usable if the device cannot open an external link.
    }
    if (!opened && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Не удалось открыть ссылку.')));
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: Text(widget.title)),
        body: SafeArea(
          child: Column(children: [
            Padding(
              padding: const EdgeInsets.all(12),
              child: Text(
                '${widget.point.latitude.toStringAsFixed(5)}, ${widget.point.longitude.toStringAsFixed(5)}'
                '\nТочность ±${widget.point.accuracy.round()} м · '
                '${widget.point.timestamp.toLocal()}',
                textAlign: TextAlign.center,
              ),
            ),
            if (_tileError)
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Text(
                    'Не удалось загрузить карту. Проверьте интернет. Координаты точки сохранены.'),
              ),
            Expanded(
              child: FlutterMap(
                mapController: _controller,
                options: MapOptions(
                  initialCenter: _position,
                  initialZoom: 16,
                  minZoom: 3,
                  maxZoom: 19,
                ),
                children: [
                  TileLayer(
                    urlTemplate: Environment.mapTileUrl,
                    userAgentPackageName: 'kg.qorgo.qorgo',
                    tileProvider: widget.tileProvider,
                    maxNativeZoom: 19,
                    panBuffer: 0,
                    errorTileCallback: (tile, error, stackTrace) {
                      if (!_tileError && mounted) {
                        WidgetsBinding.instance.addPostFrameCallback((_) {
                          if (mounted) setState(() => _tileError = true);
                        });
                      }
                    },
                  ),
                  if (widget.point.accuracy.isFinite &&
                      widget.point.accuracy > 0)
                    CircleLayer(circles: [
                      CircleMarker(
                        point: _position,
                        radius: widget.point.accuracy,
                        useRadiusInMeter: true,
                        color: const Color(0x22235D3B),
                        borderColor: QorgoDesign.green,
                        borderStrokeWidth: 1,
                      ),
                    ]),
                  MarkerLayer(markers: [
                    Marker(
                      point: _position,
                      width: 48,
                      height: 48,
                      child: Semantics(
                        label: widget.title,
                        child: const Icon(Icons.location_pin,
                            size: 48, color: QorgoDesign.danger),
                      ),
                    ),
                  ]),
                  SimpleAttributionWidget(
                    source: Text(Environment.mapAttribution),
                    onTap: () =>
                        _open('https://www.openstreetmap.org/copyright'),
                  ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(12),
              child:
                  Wrap(alignment: WrapAlignment.center, spacing: 12, children: [
                FilledButton.icon(
                  onPressed: () => _controller.move(_position, 16),
                  icon: const Icon(Icons.my_location),
                  label: const Text('К точке'),
                ),
                TextButton.icon(
                  onPressed: () => _open(widget.point.mapUrl),
                  icon: const Icon(Icons.open_in_new),
                  label: const Text('Открыть в браузере'),
                ),
              ]),
            ),
          ]),
        ),
      );
}
