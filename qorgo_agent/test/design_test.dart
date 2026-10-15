import 'package:flutter_test/flutter_test.dart';
import 'package:qorgo_agent/core/design.dart';

void main() {
  test('agent uses the QORGO dark emergency palette', () {
    expect(AgentDesign.background.toARGB32(), 0xFF030705);
    expect(AgentDesign.danger.toARGB32(), 0xFFD34C43);
  });
}
