import 'package:flutter_bloc/flutter_bloc.dart';
import 'dart:async';

part 'animal_summary_state.dart';

class AnimalSummaryCubit extends Cubit<AnimalSummaryState> {
  AnimalSummaryCubit() : super(AnimalSummaryInitial());

  // Mock data provider
  final Map<String, AnimalDetails> _mockDatabase = {
    '1': AnimalDetails(
      id: '1',
      name: 'Bessie',
      imageUrl: "https://images.unsplash.com/photo-1527153857715-3908f2bae5e8?q=80&w=1988&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      status: AnimalStatus.allGood,
      healthEntries: [],
      weight: 450.5,
      age: 36,
    ),
    '2': AnimalDetails(
      id: '2',
      name: 'Daisy',
      imageUrl: "https://images.unsplash.com/photo-1527153857715-3908f2bae5e8?q=80&w=1988&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      status: AnimalStatus.needsAttention,
      healthEntries: [
        ProblemSolutionEntry(
          problem: 'Reduced appetite',
          solution: 'Adjust feed mixture',
          status: 'In Progress',
        ),
        ProblemSolutionEntry(
          problem: 'Lower milk yield',
          solution: 'Check for signs of stress',
          status: 'Pending',
        ),
      ],
      weight: 425.0,
      age: 48,
    ),
    '3': AnimalDetails(
      id: '3',
      name: 'Luna',
      imageUrl: "https://images.unsplash.com/photo-1527153857715-3908f2bae5e8?q=80&w=1988&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      status: AnimalStatus.needsImmediateAttention,
      healthEntries: [
        ProblemSolutionEntry(
          problem: 'Fever',
          solution: 'Immediate veterinary consultation',
          status: 'Critical',
        ),
        ProblemSolutionEntry(
          problem: 'Not eating properly',
          solution: 'Isolation from herd',
          status: 'In Progress',
        ),
        ProblemSolutionEntry(
          problem: 'Reduced movement',
          solution: 'Temperature monitoring',
          status: 'Pending',
        ),
      ],
      weight: 380.5,
      age: 24,
    ),
  };

  Future<void> fetchAnimalDetails(String bovineId) async {
    emit(AnimalSummaryLoading());
    try {
      await Future.delayed(const Duration(seconds: 1));
      final animal = _mockDatabase[bovineId];
      if (animal != null) {
        emit(AnimalSummaryLoaded(animal));
      } else {
        emit(AnimalSummaryError('Animal not found'));
      }
    } catch (e) {
      emit(AnimalSummaryError('Failed to fetch animal details'));
    }
  }
}