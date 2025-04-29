part of 'login_cubit.dart';

abstract class LoginState {}

class LoginInitial extends LoginState {}

class LoginLoading extends LoginState {}

class LoginSuccess extends LoginState {
  final String username;
  final int user_id;
  final String jwt;
  LoginSuccess({required this.username, required this.user_id, required this.jwt});
}

class LoginError extends LoginState {
  final String message;
  LoginError(this.message);
}
