import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../data/datasources/profile_remote_data_source.dart';
import '../../domain/entities/similar_user.dart';

part 'profile_event.dart';
part 'profile_state.dart';

class ProfileBloc extends Bloc<ProfileEvent, ProfileState> {
  final ProfileRemoteDataSource _dataSource;

  ProfileBloc(this._dataSource) : super(ProfileInitial()) {
    on<ProfileLoadRequested>(_onLoad);
  }

  Future<void> _onLoad(ProfileLoadRequested event, Emitter<ProfileState> emit) async {
    emit(ProfileLoading());
    try {
      final users = await _dataSource.getSimilarUsers(event.userId);
      emit(ProfileLoaded(users));
    } catch (e) {
      emit(ProfileError(e.toString()));
    }
  }
}
