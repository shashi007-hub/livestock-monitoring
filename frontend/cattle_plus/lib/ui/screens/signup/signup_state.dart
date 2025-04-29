part of 'signup_cubit.dart';

abstract class SignupState {}

class SignupInitial extends SignupState {}

class SignupLoading extends SignupState {}

class SignupSuccess extends SignupState {
  final String username;
  SignupSuccess(this.username);
}

class SignupError extends SignupState {
  final String message;
  SignupError(this.message);
}