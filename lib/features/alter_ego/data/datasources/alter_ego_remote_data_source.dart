import 'package:dio/dio.dart';
import '../../domain/entities/alter_ego.dart';

class AlterEgoRemoteDataSource {
  final Dio _dio;
  AlterEgoRemoteDataSource(this._dio);

  Future<AlterEgo> generate({required String selfieUrl, required String universe}) async {
    final response = await _dio.post('/alter-ego/generate', data: {
      'selfie_url': selfieUrl,
      'universe': universe,
    });
    return AlterEgo.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> like(String alterEgoId) async {
    await _dio.post('/alter-ego/$alterEgoId/like');
  }

  Future<void> delete(String alterEgoId) async {
    await _dio.delete('/alter-ego/$alterEgoId');
  }
}
