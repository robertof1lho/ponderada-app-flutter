abstract class Failure {
  final String message;
  const Failure(this.message);
}

class NetworkFailure extends Failure {
  const NetworkFailure(super.message);
}

class AuthFailure extends Failure {
  const AuthFailure(super.message);
}

class GenerationFailure extends Failure {
  const GenerationFailure(super.message);
}

class UnknownFailure extends Failure {
  const UnknownFailure(super.message);
}
