import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:cattle_plus/global_state/language_cubit/language_cubit.dart';
import 'package:cattle_plus/labels.dart';  

extension TranslationExtension on BuildContext {
  String tr(String key) {
    final languageState = read<LanguageCubit>().state;
    final languageCode = (languageState as LanguageChanged).languageCode;
    return Labels.translate(key, languageCode);
  }
}