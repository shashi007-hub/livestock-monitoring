
sealed class SplashState  {
}

class SplashInitial extends SplashState {}

class SplashLoading extends SplashState {}

class SplashSuccess extends SplashState {}

class SplashError extends SplashState {
  final String message;
  SplashError(this.message);
}

class SplashShowAuthOptions extends SplashState {}

