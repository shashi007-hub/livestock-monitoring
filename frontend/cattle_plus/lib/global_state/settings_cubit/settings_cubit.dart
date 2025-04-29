import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'settings_state.dart';

class SettingsCubit extends Cubit<SettingsState> {
  SettingsCubit() : super(SettingsInitial());

  Future<void> logout() async {
    try {
      emit(SettingsLoading());
      print('Logging out...');
      final authBox = Hive.box('authBox');
      await authBox.clear(); // Clear auth data
      print('Auth data cleared.');
      emit(SettingsSuccess());
    } catch (e) {
      emit(SettingsError('Failed to logout: $e'));
    }
  }
}