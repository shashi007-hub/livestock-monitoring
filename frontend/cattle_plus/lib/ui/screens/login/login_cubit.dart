import 'package:cattle_plus/env.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;

part 'login_state.dart';

class LoginCubit extends Cubit<LoginState> {
  LoginCubit() : super(LoginInitial());

  Future<void> login(String username, String password) async {
    emit(LoginLoading());
    try {
      final response = await http.post(
        Uri.parse('http://$SERVER_URL/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          "username": username,
          "password": password
        }),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(response.body);
        final String jwt = data['access_token'];
        final int userId = data['user_id'];
        await _saveAuthData(username, userId, jwt);
        emit(LoginSuccess(username: username, user_id: userId, jwt: jwt));
      } else {
        emit(LoginError("Invalid username or password."));
      }
    } catch (e) {
      emit(LoginError("An error occurred during login. Please try again."));
    }
  }

  Future<void> _saveAuthData(String username,int user_id ,String jwt) async {
    final box = await Hive.openBox('authBox');
    await box.put('username', username);
    await box.put('user_id', user_id);
    await box.put('jwt', jwt);
  }

  Future<void> logout() async {
    final box = await Hive.openBox('authBox');
    await box.clear();
    emit(LoginInitial());
  }
}



//Login API - /login - POST
// Req body
// {
//     "username":"shreyas",
//     "password":"skiosxjioji"
// }
// Res body
// {
//     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzaHJleWFzIiwiZXhwIjoxNzUxMjYxOTAwfQ.v7TwUh7tOwp1q760HmbReru1cjAvDB0mjoDo9VLoKUQ",
//     "token_type": "bearer",
//     "user_id": 2,
//     "username": "shreyas"
// }