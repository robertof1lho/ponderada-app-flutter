import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../data/datasources/alter_ego_remote_data_source.dart';
import '../../domain/entities/alter_ego.dart';
import '../../../../core/errors/error_handler.dart';

part 'alter_ego_event.dart';
part 'alter_ego_state.dart';

class AlterEgoBloc extends Bloc<AlterEgoEvent, AlterEgoState> {
  final AlterEgoRemoteDataSource _dataSource;

  AlterEgoBloc(this._dataSource) : super(AlterEgoInitial()) {
    on<GenerateRequested>(_onGenerate);
    on<LikeRequested>(_onLike);
    on<DeleteRequested>(_onDelete);
  }

  Future<void> _onGenerate(GenerateRequested event, Emitter<AlterEgoState> emit) async {
    emit(AlterEgoGenerating());
    try {
      final result = await _dataSource.generate(
        selfieUrl: event.selfieUrl,
        universe: event.universe,
      );
      emit(AlterEgoGenerated(result));
    } catch (e) {
      emit(AlterEgoError(friendlyError(e)));
    }
  }

  Future<void> _onLike(LikeRequested event, Emitter<AlterEgoState> emit) async {
    try {
      await _dataSource.like(event.alterEgoId);
    } catch (_) {}
  }

  Future<void> _onDelete(DeleteRequested event, Emitter<AlterEgoState> emit) async {
    try {
      await _dataSource.delete(event.alterEgoId);
      emit(AlterEgoDeleted());
    } catch (e) {
      emit(AlterEgoError(friendlyError(e)));
    }
  }
}
