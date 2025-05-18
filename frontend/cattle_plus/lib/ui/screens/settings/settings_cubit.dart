import 'package:bloc/bloc.dart';
import 'settings_state.dart';

class SettingsCubit extends Cubit<SettingsState> {
  SettingsCubit() : super(SettingsInitial());

  // Example logout function simulating async operation
  Future<void> logout() async {
    emit(SettingsLoading());
    try {
      // Simulate a network call or logout logic
      await Future.delayed(const Duration(seconds: 2));

      // On success
      emit(SettingsSuccess());
    } catch (e) {
      // On error
      emit(SettingsError('Failed to logout. Please try again.'));
    }
  }
}
