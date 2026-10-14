import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:qorgo/domain/entities.dart';
import 'package:qorgo/feature/maps/map_view.dart';

class _TestTiles extends TileProvider {
  @override
  ImageProvider getImage(TileCoordinates coordinates, TileLayer options) =>
      MemoryImage(base64Decode(
          'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII='));
}

void main() {
  test('SOS links use OpenStreetMap with the actual coordinates', () {
    final point = GeoPoint(-1.2, 72.8161, 12, DateTime.utc(2026));
    final url = Uri.parse(point.mapUrl);
    expect(url.host, 'www.openstreetmap.org');
    expect(url.queryParameters['mlat'], '-1.2');
    expect(url.queryParameters['mlon'], '72.8161');
  });
  testWidgets('Map shows SOS coordinates and can recenter after a drag',
      (tester) async {
    final point = GeoPoint(40.5133, 72.8161, 15, DateTime.utc(2026));
    await tester.pumpWidget(MaterialApp(
        home: OpenStreetMapView(
            point: point, title: 'Место SOS', tileProvider: _TestTiles())));
    await tester.pumpAndSettle();
    expect(find.textContaining('40.51330, 72.81610'), findsOneWidget);
    expect(find.text('© OpenStreetMap contributors'), findsOneWidget);
    final context = tester.element(find.byType(MarkerLayer));
    expect(MapCamera.of(context).center.latitude, closeTo(40.5133, 0.00001));
    await tester.drag(find.byType(FlutterMap), const Offset(120, 60));
    await tester.pumpAndSettle();
    expect(MapCamera.of(context).center.latitude,
        isNot(closeTo(40.5133, 0.00001)));
    await tester.tap(find.text('К точке'));
    await tester.pumpAndSettle();
    expect(MapCamera.of(context).center.latitude, closeTo(40.5133, 0.00001));
    expect(MapCamera.of(context).center.longitude, closeTo(72.8161, 0.00001));
    expect(tester.takeException(), isNull);
  });
}
