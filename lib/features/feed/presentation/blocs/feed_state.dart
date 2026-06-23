part of 'feed_bloc.dart';

abstract class FeedState extends Equatable {
  const FeedState();
  @override
  List<Object> get props => [];
}

class FeedInitial extends FeedState {}
class FeedLoading extends FeedState {}

class FeedLoaded extends FeedState {
  final List<FeedItem> items;
  const FeedLoaded(this.items);
  @override
  List<Object> get props => [items];
}

class FeedError extends FeedState {
  final String message;
  const FeedError(this.message);
  @override
  List<Object> get props => [message];
}
