import 'package:flutter_test/flutter_test.dart';
import 'package:robolab_mobile/main.dart';

void main() {
  testWidgets('RoboLab workspace renders', (tester) async {
    await tester.pumpWidget(const RoboLabApp());
    expect(find.text('Engineering Workspace'), findsOneWidget);
    expect(find.text('One project → requirements → architecture → circuit → code → verification → compile gate.'), findsOneWidget);
  });
}
