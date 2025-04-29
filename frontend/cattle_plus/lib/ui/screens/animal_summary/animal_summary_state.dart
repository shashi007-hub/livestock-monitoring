part of 'animal_summary_cubit.dart';

enum AnimalStatus {
  needsImmediateAttention,
  needsAttention,
  allGood
}

class ProblemSolutionEntry {
  final String problem;
  final String solution;
  final String status;

  ProblemSolutionEntry({
    required this.problem,
    required this.solution,
    required this.status,
  });
}

class AnimalDetails {
  final String id;
  final String name;
  final String imageUrl;
  final AnimalStatus status;
  final List<ProblemSolutionEntry> healthEntries;
  final double weight;
  final int age;

  AnimalDetails({
    required this.id,
    required this.name,
    required this.imageUrl,
    required this.status,
    required this.healthEntries,
    required this.weight,
    required this.age,
  });
}

abstract class AnimalSummaryState {}

class AnimalSummaryInitial extends AnimalSummaryState {}

class AnimalSummaryLoading extends AnimalSummaryState {}

class AnimalSummaryLoaded extends AnimalSummaryState {
  final AnimalDetails animal;
  AnimalSummaryLoaded(this.animal);
}

class AnimalSummaryError extends AnimalSummaryState {
  final String message;
  AnimalSummaryError(this.message);
}