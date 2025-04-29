import 'package:bloc/bloc.dart';
import 'package:meta/meta.dart';

part 'language_state.dart';

class LanguageCubit extends Cubit<LanguageState> {
  LanguageCubit() : super(LanguageChanged("en"));

  getLanguage() {
    return state.getLanguage();
  }

  void changeLanguage(String languageCode) {
    emit(LanguageChanged(languageCode));
  }

  void resetLanguage() {
    emit(LanguageChanged("en"));
  }

}
