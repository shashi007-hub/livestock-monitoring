abstract class AddAnimalState {}

class AddAnimalInitial extends AddAnimalState {}

class AddAnimalLoading extends AddAnimalState {}

class AddAnimalSuccess extends AddAnimalState {}

class AddAnimalError extends AddAnimalState {
  final String message;
  AddAnimalError(this.message);
}