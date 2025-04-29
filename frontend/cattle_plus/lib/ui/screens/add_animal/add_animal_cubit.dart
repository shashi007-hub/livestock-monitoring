import 'dart:convert';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'add_animal_states.dart';
import 'package:http/http.dart' as http;
import 'package:cattle_plus/env.dart';

class AddAnimalCubit extends Cubit<AddAnimalState> {
  AddAnimalCubit() : super(AddAnimalInitial());

  Future<void> addBovine({
    required String name,
    required int age,
    required double weight,
    required String breed,
    String? fatherId,
    String? motherId,
    required String imageBase64,
  }) async {
    print(name);
    print(age);
    print(weight);
    print(breed);
    print(fatherId);
    print(motherId);
    print(imageBase64);
    try {
      emit(AddAnimalLoading());
      
      final box = await Hive.openBox('authBox');
      final userId = int.parse(box.get('user_id',defaultValue: 1)) ;
      

      final response = await http.post(
        Uri.parse('http://$SERVER_URL/bovines/'),
        body: jsonEncode({
          'name': name,
          'age': age,
          'weight': weight,
          'breed': breed,
          'image_base64': imageBase64,
          'owner_id': userId,
        }),
        headers: {'Content-Type': 'application/json'},
      );
      print(response.body);
      print(response.statusCode);

      if (response.statusCode == 200 || response.statusCode == 201) {
        emit(AddAnimalSuccess());
      } else {
        emit(AddAnimalError('Failed to add bovine: ${response.body}'));
      }
    } catch (e) {
      print(e.toString());
      emit(AddAnimalError('Failed to add bovine: $e'));
    }
  }
}

// Valid breed types
enum BreedType {
  GIR,
  SAHIWAL,
  THARPARKAR,
  RATHI,
  KANKREJ,
  RED_SINDHI,
  ONGOLE,
  KANGAYAM,
  HALLIKAR,
  OTHER
}

extension BreedTypeExtension on BreedType {
  String get displayName {
    switch (this) {
      case BreedType.GIR:
        return "Gir";
      case BreedType.SAHIWAL:
        return "Sahiwal";
      case BreedType.THARPARKAR:
        return "Tharparkar";
      case BreedType.RATHI:
        return "Rathi";
      case BreedType.KANKREJ:
        return "Kankrej";
      case BreedType.RED_SINDHI:
        return "Red Sindhi";
      case BreedType.ONGOLE:
        return "Ongole";
      case BreedType.KANGAYAM:
        return "Kangayam";
      case BreedType.HALLIKAR:
        return "Hallikar";
      case BreedType.OTHER:
        return "Other";
    }
  }
}