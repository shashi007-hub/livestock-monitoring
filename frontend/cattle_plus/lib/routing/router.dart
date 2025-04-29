import 'package:cattle_plus/ui/screen_container.dart';
import 'package:cattle_plus/ui/screens/login/login_screen.dart';
import 'package:cattle_plus/ui/screens/splash/splash_screen.dart';
import 'package:cattle_plus/ui/screens/signup/signup_screen.dart';
import 'package:cattle_plus/ui/screens/settings/settings.dart';
import 'package:cattle_plus/ui/screens/animal_summary/animal_summary.dart';
import 'package:flutter/material.dart';
import 'routes.dart';

class AppRouter {
  Route? onGenerateRoute(RouteSettings routeSettings) {
    switch (routeSettings.name?.split('?')[0]) {
      case Routes.SPLASH:
        return MaterialPageRoute(builder: (context) =>  SplashScreen());
      case Routes.LOGIN:
        return MaterialPageRoute(builder: (context) =>  LoginScreen());
      case Routes.SIGNUP:
        return MaterialPageRoute(builder: (context) =>  SignupScreen());
      case Routes.HOME:
        return MaterialPageRoute(builder: (context) => ScreenContainer());
      case Routes.SETTINGS:
        return MaterialPageRoute(builder: (context) =>  SettingsUI());
      case Routes.ADD_ANIMAL:
        return MaterialPageRoute(builder: (context)=> Placeholder());
      case Routes.ANIMAL_SUMMARY:
        // Extract bovineId from route settings arguments or query parameters
        final bovineId = (routeSettings.arguments as String?) ?? 
                        Uri.parse(routeSettings.name!).queryParameters['id'] ?? 
                        '1'; // Default to '1' if no ID provided
        return MaterialPageRoute(
          builder: (context) => AnimalSummaryScreen(bovineId: bovineId),
        );
      case Routes.ANIMAL_INSIGHTS:
      case Routes.ANIMAL_TRACKING:
      default:
        // Return a default screen for unimplemented or missing routes
        return MaterialPageRoute(
          builder: (context) => Scaffold(
            appBar: AppBar(
              title: Text(routeSettings.name?.substring(1) ?? 'Not Found'),
              leading: BackButton(onPressed: () => Navigator.of(context).pop()),
            ),
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.construction, size: 64, color: Colors.orange),
                  const SizedBox(height: 16),
                  Text(
                    'Screen ${routeSettings.name} is under construction',
                    style: Theme.of(context).textTheme.titleLarge,
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          ),
        );
    }
  }
}