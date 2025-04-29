import 'package:cattle_plus/global_state/language_cubit/language_cubit.dart';
import 'package:cattle_plus/global_state/settings_cubit/settings_cubit.dart';
import 'package:cattle_plus/routing/router.dart';
import 'package:cattle_plus/theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Hive.initFlutter();
  await Hive.openBox('authBox'); // Initialize the auth box
  await Hive.openBox('settingsBox');
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  MyApp({super.key});
  final AppRouter appRouter = AppRouter();

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider<LanguageCubit>(create: (context) => LanguageCubit()),
        BlocProvider<SettingsCubit>(create: (context) => SettingsCubit()),
      ],
      child: MaterialApp(
        onGenerateRoute: appRouter.onGenerateRoute,
        theme: appTheme,
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}
