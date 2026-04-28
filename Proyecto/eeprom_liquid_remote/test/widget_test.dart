// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';

import 'package:eeprom_liquid_remote/main.dart';

void main() {
  testWidgets('renders smart home control panel', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1080, 1920);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);

    await tester.pumpWidget(const SmartHomeApp());
    await tester.pumpAndSettle();

    expect(find.text('EEPROM Liquid Remote'), findsOneWidget);
    expect(find.text('Modo Actual'), findsOneWidget);
    expect(find.text('Sistema No Disponible'), findsOneWidget);
    expect(find.text('Modo Fiesta'), findsOneWidget);
  });
}
