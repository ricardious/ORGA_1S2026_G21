// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter_test/flutter_test.dart';

import 'package:eeprom_liquid_remote/main.dart';

void main() {
  testWidgets('renders smart home control panel', (WidgetTester tester) async {
    await tester.pumpWidget(const SmartHomeApp());

    expect(find.text('Control Center'), findsOneWidget);
    expect(find.text('Modo Actual'), findsOneWidget);
    expect(find.text('Sistema Listo'), findsOneWidget);
    expect(find.text('Comandos Principales'), findsNothing);
  });
}
