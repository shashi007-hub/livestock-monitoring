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
    if (user != null && jwt != null) {
      emit(SplashSuccess());
    } else {
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
