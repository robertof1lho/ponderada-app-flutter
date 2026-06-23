import 'package:dio/dio.dart';
import '../../domain/entities/feed_item.dart';

class FeedRemoteDataSource {
  final Dio _dio;
  FeedRemoteDataSource(this._dio);

  Future<List<FeedItem>> getFeed({int limit = 20, int offset = 0}) async {
    final response = await _dio.get('/feed', queryParameters: {'limit': limit, 'offset': offset});
    final list = response.data as List<dynamic>;
    return list.map((e) => FeedItem.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<void> deleteAlterEgo(String alterEgoId) async {
    await _dio.delete('/alter-ego/$alterEgoId');
  }
}
