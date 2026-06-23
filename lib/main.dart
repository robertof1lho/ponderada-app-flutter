import 'package:flutter/material.dart';
import 'core/auth/auth_service.dart';
import 'core/di/injection.dart';
import 'core/router/app_router.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AuthService.load();
  setupDependencies();
  runApp(const AlterMeApp());
}

class AlterMeApp extends StatelessWidget {
  const AlterMeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'AlterMe',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF6C63FF)),
        useMaterial3: true,
      ),
      routerConfig: AppRouter.router,
    );
  }
}
