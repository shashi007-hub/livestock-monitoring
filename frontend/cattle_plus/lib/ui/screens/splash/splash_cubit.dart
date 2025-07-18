import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:http/http.dart' as http;
import 'dart:async';
import '../../../env.dart';
import 'splash_state.dart';

class SplashCubit extends Cubit<SplashState> {
  SplashCubit() : super(SplashInitial());

  Future<void> initialize() async {
    emit(SplashLoading());
    await Future.delayed(const Duration(milliseconds: 800));
    // Check server connectivity
    final serverOk = await checkServerConnectivity();
    if (!serverOk) {
      emit(
        SplashError('Cannot connect to server. Please check your connection.'),
      );
      return;
    }
    // 1) Check Hive for user/jwt
    final box = await Hive.openBox('authBox');
    final user = box.get('username');
    final jwt = box.get('jwt');
    final logoutPerformed = box.get('logout_performed');

    print(
      'Splash initialization - User: $user, JWT: ${jwt != null ? "present" : "null"}, LogoutFlag: $logoutPerformed',
    );

    // If logout was performed, clear the flag and show auth options
    if (logoutPerformed == true) {
      await box.delete('logout_performed');
      print('Logout flag detected and cleared, showing auth options');
      emit(SplashShowAuthOptions());
      return;
    }

    if (user != null && jwt != null) {
      print('Valid auth data found, navigating to home');
      emit(SplashSuccess());
    } else {
      print('No valid auth data found, showing auth options');
      emit(SplashShowAuthOptions());
    }
  }

  Future<bool> checkServerConnectivity() async {
    try {
      print("SERVER_URL: '$SERVER_URL'");
      print("Attempting to connect to server at: http://$SERVER_URL/health");
      final response = await http.get(Uri.parse('http://$SERVER_URL/health'));
      return response.statusCode == 200;
    } catch (e) {
      print(e);
      return false;
    }
  }

  void retry() {
    initialize();
  }
}
