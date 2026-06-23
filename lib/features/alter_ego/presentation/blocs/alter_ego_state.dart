part of 'alter_ego_bloc.dart';

abstract class AlterEgoState extends Equatable {
  const AlterEgoState();
  @override
  List<Object> get props => [];
}

class AlterEgoInitial extends AlterEgoState {}
class AlterEgoGenerating extends AlterEgoState {}

class AlterEgoGenerated extends AlterEgoState {
  final AlterEgo alterEgo;
  const AlterEgoGenerated(this.alterEgo);
  @override
  List<Object> get props => [alterEgo.id];
}

class AlterEgoError extends AlterEgoState {
  final String message;
  const AlterEgoError(this.message);
  @override
  List<Object> get props => [message];
}

class AlterEgoDeleted extends AlterEgoState {}
