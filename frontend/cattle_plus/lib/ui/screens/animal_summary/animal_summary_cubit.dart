import 'dart:convert';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:cattle_plus/env.dart';
import 'package:http/http.dart' as http;

part 'animal_summary_state.dart';

class AnimalSummaryCubit extends Cubit<AnimalSummaryState> {
  AnimalSummaryCubit() : super(AnimalSummaryInitial());

  final String apiUrl =
      "http://your-server-url/api/animals"; // Replace with your real endpoint

  Future<void> fetchAnimalDetails(String bovineId) async {
    emit(AnimalSummaryLoading());
    try {
      // Uncomment the below line to use real API
      final response = await http.get(
        Uri.parse('http://$SERVER_URL/bovines/$bovineId/details'),
      );
      print("response for animal details");
      print(response.body);
      final mock = {
        "id": bovineId,
        "name": "Bovine $bovineId",
        "imageUrl": "https://via.placeholder.com/200",
        "status": "needsImmediateAttention",
        "healthEntries": [
          {"problem": "None", "solution": "N/A", "status": "Resolved"},
        ],
        "weight": 450.5,
        "age": 5,
        "feeding_analysis": [
          {"date": "2023-01-01", "avg": 5.5},
          {"date": "2023-01-02", "avg": 7.0},
          {"date": "2023-01-03", "avg": 5.8},
          {"date": "2023-01-04", "avg": 6.2},
          {"date": "2023-01-05", "avg": 5.9},
        ],
      };
      final status = response.statusCode; // Mock response status code
      if (status == 200) {
        final data = json.decode(response.body);

        final animal = AnimalDetails(
          id: data['id'].toString(),
          name: data['name'].toString(),
          imageUrl: data['imageUrl'].toString(),
          status: AnimalStatus.values.firstWhere(
            (e) => e.toString() == 'AnimalStatus.${data['status']}',
          ),
          healthEntries:
              (data['healthEntries'] as List?)
                  ?.map(
                    (entry) => ProblemSolutionEntry(
                      problem: entry['problem'],
                      solution: entry['solution'],
                      status: entry['status'],
                    ),
                  )
                  .toList() ??
              [],
          weight: (data['weight'] as num?)!.toDouble(),
          age: (data['age'] as num?)?.toInt() ?? 0,
          feedingAnalysis:
              (data['feeding_analysis'] != null &&
                      (data['feeding_analysis'] as List).isNotEmpty)
                  ? (data['feeding_analysis'] as List)
                      .map(
                        (entry) => FeedingAnalysis(
                          date: entry['date'].toString(),
                          avg: (entry['avg'] as num).toDouble(),
                        ),
                      )
                      .toList()
                  : [],
        );

        emit(
          AnimalSummaryLoaded(
            animal: animal,
            feedingAnalysis: animal.feedingAnalysis,
          ),
        );
      } else {
        emit(AnimalSummaryError('Failed to fetch animal details'));
      }
    } catch (e) {
      emit(AnimalSummaryError('Failed to fetch animal details: $e'));
    }
  }
}

String getBovineImageUrl(int bovineId) {
  return 'http://$SERVER_URL/bovines/$bovineId/image';
}
