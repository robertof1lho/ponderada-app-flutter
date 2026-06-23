part of 'alter_ego_bloc.dart';

abstract class AlterEgoEvent extends Equatable {
  const AlterEgoEvent();
  @override
  List<Object> get props => [];
}

class GenerateRequested extends AlterEgoEvent {
  final String selfieUrl;
  final String universe;
  const GenerateRequested({required this.selfieUrl, required this.universe});
  @override
  List<Object> get props => [selfieUrl, universe];
}

class LikeRequested extends AlterEgoEvent {
  final String alterEgoId;
  const LikeRequested(this.alterEgoId);
  @override
  List<Object> get props => [alterEgoId];
}

class DeleteRequested extends AlterEgoEvent {
  final String alterEgoId;
  const DeleteRequested(this.alterEgoId);
  @override
  List<Object> get props => [alterEgoId];
}
