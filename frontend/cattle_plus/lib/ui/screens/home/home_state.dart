part of 'home_cubit.dart';

class Bovine {
  final String name;
  final int age;
  final double weight;
  final String breed;
  final String location;
  final int? fatherId;
  final int? motherId;
  final int id;

  const Bovine({
    required this.name,
    required this.age,
    required this.weight,
    required this.breed,
    required this.location,
    this.fatherId,
    this.motherId,
    required this.id,
  });

  factory Bovine.fromJson(Map<String, dynamic> json) {
    return Bovine(
      name: json['name'],
      age: json['age'],
      weight: json['weight'].toDouble(),
      breed: json['breed'],
      location: json['location'],
      fatherId: json['father_id'],
      motherId: json['mother_id'],
      id: json['id'],
    );
  }
}

class BovineStatus {
  final int bovineId;
  final String status;

  const BovineStatus({required this.bovineId, required this.status});

  factory BovineStatus.fromJson(Map<String, dynamic> json) {
    return BovineStatus(bovineId: json['bovine_id'], status: json['status']);
  }
}

abstract class HomeState {
  final String username;
  final String city;
  final int anomalies;
  final int averageSteps;
  final int grazingVolume;
  final List<Bovine> bovines;
  final List<BovineStatus> statuses;

  const HomeState({
    this.username = '',
    this.city = '',
    this.anomalies = 0,
    this.averageSteps = 0,
    this.grazingVolume = 0,
    this.bovines = const [],
    this.statuses = const [],
  });
}

class HomeInitial extends HomeState {
  const HomeInitial() : super();
}

class HomeLoading extends HomeState {
  const HomeLoading() : super();
}

class HomeLoaded extends HomeState {
  const HomeLoaded({
    required String username,
    required String city,
    required int anomalies,
    required int averageSteps,
    required int grazingVolume,
    required List<Bovine> bovines,
    required List<BovineStatus> statuses,
  }) : super(
         username: username,
         city: city,
         anomalies: anomalies,
         averageSteps: averageSteps,
         grazingVolume: grazingVolume,
         bovines: bovines,
         statuses: statuses,
       );
}

class HomeError extends HomeState {
  final String errorMessage;

  const HomeError({
    required this.errorMessage,
    required String username,
    required String city,
    required int anomalies,
    required int averageSteps,
    required int grazingVolume,
    List<Bovine> bovines = const [],
    List<BovineStatus> statuses = const [],
  }) : super(
         username: username,
         city: city,
         anomalies: anomalies,
         averageSteps: averageSteps,
         grazingVolume: grazingVolume,
         bovines: bovines,
         statuses: statuses,
       );
}
