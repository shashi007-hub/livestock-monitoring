import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'settings_state.dart';

class SettingsCubit extends Cubit<SettingsState> {
  SettingsCubit() : super(SettingsInitial());

  Future<void> logout() async {
    try {
      emit(SettingsLoading());
      print('Logging out...');

      // Clear auth data from Hive
      final authBox = await Hive.openBox('authBox');

      // Log what's being cleared
      final username = authBox.get('username');
      final jwt = authBox.get('jwt');
      final userId = authBox.get('user_id');
      final city = authBox.get('city');

      print(
        'Clearing auth data - Username: $username, JWT: ${jwt != null ? "present" : "null"}, UserID: $userId, City: $city',
      );

      // Clear all authentication-related data
      await authBox.delete('username');
      await authBox.delete('jwt');
      await authBox.delete('user_id');
      await authBox.delete('city');
      await authBox.delete('token');
      await authBox.delete('refresh_token');

      // Also try clearing the entire box as a fallback
      await authBox.clear();

      // Add a logout flag to indicate logout was performed
      await authBox.put('logout_performed', true);

      // Add a small delay to ensure the logout flag is properly written
      await Future.delayed(const Duration(milliseconds: 100));

      // Close and reopen the box to ensure fresh state
      await authBox.close();
      await Future.delayed(const Duration(milliseconds: 100));
      final freshBox = await Hive.openBox('authBox');

      // Also clear settings box to be safe
      try {
        final settingsBox = await Hive.openBox('settingsBox');
        await settingsBox.clear();
        await settingsBox.close();
        print('Settings box cleared');
      } catch (e) {
        print('Error clearing settings box: $e');
      }

      // Clear any other potential Hive boxes
      try {
        // Try to clear any other boxes that might exist
        final otherBoxes = ['userBox', 'cacheBox', 'preferencesBox'];
        for (final boxName in otherBoxes) {
          try {
            final box = await Hive.openBox(boxName);
            await box.clear();
            await box.close();
            print('Cleared box: $boxName');
          } catch (e) {
            // Box doesn't exist, ignore
          }
        }
      } catch (e) {
        print('Error clearing other boxes: $e');
      }

      // Verify data is cleared
      final clearedUsername = freshBox.get('username');
      final clearedJwt = freshBox.get('jwt');
      final clearedUserId = freshBox.get('user_id');
      final clearedCity = freshBox.get('city');
      final logoutFlag = freshBox.get('logout_performed');

      print(
        'After clearing - Username: $clearedUsername, JWT: $clearedJwt, UserID: $clearedUserId, City: $clearedCity, LogoutFlag: $logoutFlag',
      );

      // Add a small delay to ensure data is properly cleared
      await Future.delayed(const Duration(milliseconds: 300));

      // Final verification
      final finalCheck = freshBox.get('username');
      final finalLogoutFlag = freshBox.get('logout_performed');
      print(
        'Final check - Username: $finalCheck, LogoutFlag: $finalLogoutFlag',
      );

      if (finalCheck == null && finalLogoutFlag == true) {
        print('Auth data cleared successfully and logout flag set.');
        emit(SettingsSuccess());
      } else {
        print('Warning: Auth data may not be fully cleared');
        emit(SettingsSuccess()); // Still proceed with logout
      }
    } catch (e) {
      print('Error during logout: $e');
      emit(SettingsError('Failed to logout: $e'));
    }
  }
}
