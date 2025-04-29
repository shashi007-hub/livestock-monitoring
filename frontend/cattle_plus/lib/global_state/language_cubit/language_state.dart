part of 'language_cubit.dart';

@immutable
sealed class LanguageState {
   String getLanguage();
}


final class LanguageChanged extends LanguageState {
  final String languageCode;

  @override
  String getLanguage() => languageCode;

  LanguageChanged(this.languageCode);
}