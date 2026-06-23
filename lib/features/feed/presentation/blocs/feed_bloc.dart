import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../data/datasources/feed_remote_data_source.dart';
import '../../domain/entities/feed_item.dart';
import '../../../../core/errors/error_handler.dart';

part 'feed_event.dart';
part 'feed_state.dart';

class FeedBloc extends Bloc<FeedEvent, FeedState> {
  final FeedRemoteDataSource _dataSource;

  FeedBloc(this._dataSource) : super(FeedInitial()) {
    on<FeedLoadRequested>(_onLoad);
  }

  Future<void> _onLoad(FeedLoadRequested event, Emitter<FeedState> emit) async {
    emit(FeedLoading());
    try {
      final items = await _dataSource.getFeed();
      emit(FeedLoaded(items));
    } catch (e) {
      emit(FeedError(friendlyError(e)));
    }
  }
}
