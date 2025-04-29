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
      final response = await http.get(Uri.parse('http://$SERVER_URL/home/2')); // Replace 1 with actual user_id
      print(response.body);
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print(data);
        final bovines = (data['bovines'] as List).map((b) => Bovine.fromJson(b)).toList();
        final statuses = (data['status'] as List).map((s) => BovineStatus.fromJson(s)).toList();
        final userName = await getUserName();
        final cityName = await getCityName();
        

        emit(HomeLoaded(
          username: userName, // This should come from user profile
          city: cityName, // This should come from user profile
          anomalies: data['anamalies'] ?? 0,
          averageSteps: data['avg_steps'] ?? 0,
          grazingVolume: data['grazing_volume'] ?? 0,
          bovines: bovines,
          statuses: statuses,
        ));
      } else {
        throw Exception('Failed to load home data');
      }
    } catch (e) {
      emit(HomeError(
        errorMessage: 'Failed to load data: ${e.toString()}',
        username: 'Srikhar',
        city: 'Hyderabad',
        anomalies: 0,
        averageSteps: 0,
        grazingVolume: 0,
      ));
    }
  }

  String getBovineImageUrl(int bovineId) {
    return 'http://$SERVER_URL/bovines/$bovineId/image';
  }

  Future<String> getUserName() async{
    final box = await Hive.openBox('authBox');
    return box.get('username') ?? "Shashi" ;
  }

  Future<String> getCityName() async{
    final box = await Hive.openBox('authBox');
    return box.get('city') ?? "Hyderabad" ;
  }
}