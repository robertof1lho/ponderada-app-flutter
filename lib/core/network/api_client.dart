import 'package:dio/dio.dart';
import 'package:go_router/go_router.dart';
import '../auth/auth_service.dart';
import '../router/app_router.dart';

class ApiClient {
  late final Dio _dio;

  static const _baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8080',
  );

  ApiClient() {
    _dio = Dio(BaseOptions(baseUrl: _baseUrl))
      ..interceptors.add(InterceptorsWrapper(
        onRequest: (options, handler) {
          final token = AuthService.token;
          if (token != null) options.headers['Authorization'] = 'Bearer $token';
          handler.next(options);
        },
        onError: (error, handler) async {
          if (error.response?.statusCode == 401) {
            await AuthService.clear();
            AppRouter.router.go('/login');
          }
          handler.next(error);
        },
      ));
  }

  Dio get dio => _dio;
}
