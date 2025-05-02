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

      // Mock response for now
      final responseStatusCode = response.statusCode;

      if (responseStatusCode == 200) {
        // final data = json.decode(response.body);
        final data1 = {
          "id": 4,
          "name": "Bessie",
          "imageUrl":
              "https://images.unsplash.com/photo-1527153857715-3908f2bae5e8?q=80&w=1988&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
          "status": "needsAttention",
          "healthEntries": [
            {
              "problem": "Reduced appetite",
              "solution": "Adjust feed mixture",
              "status": "In Progress",
            },
            {
              "problem": "Lower milk yield",
              "solution": "Check for signs of stress",
              "status": "Pending",
            },
          ],
          "weight": 450.5,
          "age": 36,
        };
        final data = json.decode(response.body);
        print(response.body);
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
        );

        emit(AnimalSummaryLoaded(animal));
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
