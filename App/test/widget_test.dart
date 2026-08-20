import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:app/main.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  sqfliteFfiInit();
  databaseFactory = databaseFactoryFfi;

  testWidgets('AquaPulseApp smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: AquaPulseApp()));
    expect(find.byType(AquaPulseApp), findsOneWidget);
  });
}
