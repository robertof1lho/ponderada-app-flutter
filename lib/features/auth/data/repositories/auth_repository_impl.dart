import 'package:dio/dio.dart';
import '../../domain/repositories/auth_repository.dart';
import '../../../../core/errors/failures.dart';
import '../../../../core/auth/auth_service.dart';
import '../../../../core/di/injection.dart';
import '../../../../core/network/api_client.dart';

class AuthRepositoryImpl implements AuthRepository {
  Dio get _dio => sl<ApiClient>().dio;

  @override
  Future<void> signIn({required String email, required String password}) async {
    try {
      final response = await _dio.post('/auth/login', data: {
        'email': email,
        'password': password,
      });
      await AuthService.save(
        response.data['id'] as String,
        response.data['token'] as String,
      );
    } on DioException catch (e) {
      final status = e.response?.statusCode;
      final detail = e.response?.data is Map ? e.response?.data['detail'] : null;
      if (status == 401 || status == 403) throw AuthFailure('E-mail ou senha incorretos.');
      if (status == 404) throw AuthFailure('Usuário não encontrado.');
      if (e.type == DioExceptionType.connectionError) throw AuthFailure('Sem conexão com o servidor.');
      throw AuthFailure(detail?.toString() ?? 'Erro ao fazer login. Tente novamente.');
    }
  }

  @override
  Future<void> signUp({required String email, required String password}) async {
    try {
      final username = email.split('@').first;
      final response = await _dio.post('/auth/register', data: {
        'username': username,
        'email': email,
        'password': password,
      });
      await AuthService.save(
        response.data['id'] as String,
        response.data['token'] as String,
      );
    } on DioException catch (e) {
      final status = e.response?.statusCode;
      final detail = e.response?.data is Map ? e.response?.data['detail'] : null;
      if (status == 409) throw AuthFailure('Este e-mail já está cadastrado.');
      if (e.type == DioExceptionType.connectionError) throw AuthFailure('Sem conexão com o servidor.');
      throw AuthFailure(detail?.toString() ?? 'Erro ao criar conta. Tente novamente.');
    }
  }

  @override
  Future<void> signOut() async {
    await AuthService.clear();
  }
}
