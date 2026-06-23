import 'package:dio/dio.dart';
import '../../domain/entities/similar_user.dart';

class ProfileRemoteDataSource {
  final Dio _dio;
  ProfileRemoteDataSource(this._dio);

  Future<List<SimilarUser>> getSimilarUsers(String userId, {int limit = 10}) async {
    final response = await _dio.get('/profile/$userId/similar', queryParameters: {'limit': limit});
    final list = response.data as List<dynamic>;
    return list.map((e) => SimilarUser.fromJson(e as Map<String, dynamic>)).toList();
  }
}
