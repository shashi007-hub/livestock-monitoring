import 'package:equatable/equatable.dart';

abstract class SettingsState extends Equatable {
  @override
  List<Object?> get props => [];
}

class SettingsInitial extends SettingsState {}

class SettingsLoading extends SettingsState {}

class SettingsSuccess extends SettingsState {}

class SettingsError extends SettingsState {
  final String message;

  SettingsError(this.message);

  @override
  List<Object?> get props => [message];
}
