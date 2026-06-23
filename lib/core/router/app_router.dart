import 'package:go_router/go_router.dart';
import '../../core/auth/auth_service.dart';
import '../../features/auth/presentation/login_screen.dart';
import '../../features/auth/presentation/register_screen.dart';
import '../../features/feed/presentation/screens/feed_screen.dart';
import '../../features/alter_ego/presentation/screens/camera_screen.dart';
import '../../features/alter_ego/presentation/screens/universe_selector_screen.dart';
import '../../features/alter_ego/presentation/screens/generating_screen.dart';
import '../../features/alter_ego/presentation/screens/result_screen.dart';

class AppRouter {
  static final router = GoRouter(
    initialLocation: '/login',
    redirect: (context, state) {
      final loggedIn = AuthService.isLoggedIn;
      final onAuth = state.matchedLocation == '/login' ||
          state.matchedLocation == '/register';
      if (!loggedIn && !onAuth) return '/login';
      if (loggedIn && onAuth) return '/home';
      return null;
    },
    routes: [
      GoRoute(path: '/login',    builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/register', builder: (_, __) => const RegisterScreen()),
      GoRoute(path: '/home',     builder: (_, __) => const FeedScreen()),
      GoRoute(path: '/feed',     builder: (_, __) => const FeedScreen()),
      GoRoute(path: '/camera',   builder: (_, __) => const CameraScreen()),
      GoRoute(
        path: '/universe',
        builder: (context, state) => const UniverseSelectorScreen(),
      ),
      GoRoute(
        path: '/generating',
        builder: (context, state) => GeneratingScreen(
          params: state.extra as Map<String, dynamic>,
        ),
      ),
      GoRoute(
        path: '/result',
        builder: (context, state) => ResultScreen(
          params: state.extra as Map<String, dynamic>,
        ),
      ),
    ],
  );
}
