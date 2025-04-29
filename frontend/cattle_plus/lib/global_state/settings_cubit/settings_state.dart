abstract class SettingsState {}

class SettingsInitial extends SettingsState {}

class SettingsLoading extends SettingsState {}

class SettingsError extends SettingsState {
  final String message;
  SettingsError(this.message);
}

class SettingsSuccess extends SettingsState {}