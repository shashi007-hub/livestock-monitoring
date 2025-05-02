import 'dart:ffi';

import 'package:bloc/bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:cattle_plus/env.dart';
part 'home_state.dart';

class HomeCubit extends Cubit<HomeState> {
  HomeCubit() : super(const HomeInitial());

  Future<void> loadHomeData() async {
    emit(const HomeLoading());

    try {
      print("sending request");
      final box = await Hive.openBox('authBox');
      final user_Id = await getUserId();
      print(user_Id);
      final userId = 2;
      final response = await http.get(
        Uri.parse('http://$SERVER_URL/home/$userId'),
      ); // Replace 1 with actual user_id
      print(response.body);
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print(data);
        print("searching for bovines");
        print(data['bovines']);
        final bovines =
            (data['bovines'] as List).map((b) => Bovine.fromJson(b)).toList();
        print("bovines");
        print(bovines);
        final statuses =
            (data['status'] as List)
                .map((s) => BovineStatus.fromJson(s))
                .toList();
        print("statuses");
        print(statuses);
        final userName = await getUserName();
        print(userName);
        final cityName = await getCityName();
        print(cityName);

        emit(
          HomeLoaded(
            username: userName, // This should come from user profile
            city: cityName, // This should come from user profile
            anomalies: data['anamalies'] ?? 100,
            averageSteps: data['avg_steps'] ?? 0,
            grazingVolume: data['grazing_volume'] ?? 0,
            bovines: bovines,
            statuses: statuses,
          ),
        );
      } else {
        throw Exception('Failed to load home data');
      }
    } catch (e) {
      print("exception");
      print(e.toString());
      emit(
        HomeError(
          errorMessage: 'Failed to load data: ${e.toString()}',
          username: 'Srikhar',
          city: 'Hyderabad',
          anomalies: 0,
          averageSteps: 0,
          grazingVolume: 0,
        ),
      );
    }
  }

  String getBovineImageUrl(int bovineId) {
    return 'http://$SERVER_URL/bovines/$bovineId/image';
  }

  Future<String> getUserName() async {
    final box = await Hive.openBox('authBox');
    return box.get('username') ?? "Shashi";
  }

  Future<String> getCityName() async {
    final box = await Hive.openBox('authBox');
    return box.get('city') ?? "Hyderabad";
  }

  Future<int> getUserId() async {
    final box = await Hive.openBox('authBox');
    return box.get('user_id') ?? 1;
  }
}
