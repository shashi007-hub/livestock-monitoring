import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'dart:async';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../../../env.dart';

part 'signup_state.dart';

class SignupCubit extends Cubit<SignupState> {
  SignupCubit() : super(SignupInitial());

  Future<void> signup(String username, String password, String phoneNumber, String city) async {
    emit(SignupLoading());
    try {
      final response = await http.post(
        Uri.parse('http://${SERVER_URL}/signup'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'username': username,
          'password': password,
          'phone_number': phoneNumber,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final accessToken = data['access_token'];

        // Store auth data and city in Hive
        await _saveAuthData(username, accessToken, city);

        emit(SignupSuccess(username));
      } else {
        emit(SignupError("Signup failed. Please try again."));
      }
    } catch (e) {
      emit(SignupError("An error occurred during signup. Please check your connection and try again."));
    }
  }

  Future<void> _saveAuthData(String username, String jwt, String city) async {
    final box = await Hive.openBox('authBox');
    await box.put('username', username);
    await box.put('jwt', jwt);
    await box.put('city', city);
  }
}