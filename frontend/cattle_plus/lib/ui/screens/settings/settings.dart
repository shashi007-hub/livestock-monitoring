import 'package:easy_localization/easy_localization.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:cattle_plus/global_state/settings_cubit/settings_cubit.dart';
import 'package:cattle_plus/global_state/settings_cubit/settings_state.dart';
import 'package:cattle_plus/routing/routes.dart';
import 'package:easy_localization/easy_localization.dart';

class SettingsUI extends StatelessWidget {
  const SettingsUI({super.key});

  @override
  Widget build(BuildContext context) {
    final currentLocale = context.locale; // Get current locale

    return BlocProvider(
      create: (context) => SettingsCubit(),
      child: BlocConsumer<SettingsCubit, SettingsState>(
        listener: (context, state) {
          if (state is SettingsError) {
            Fluttertoast.showToast(
              msg: state.message,
              backgroundColor: Colors.red,
              textColor: Colors.white,
            );
          } else if (state is SettingsSuccess) {
            print('Logging out - navigating to splash screen');
            // Clear all routes and navigate to splash
            Navigator.pushNamedAndRemoveUntil(
              context,
              Routes.SPLASH,
              (route) => false,
            );
          }
        },
        builder: (context, state) {
          return SafeArea(
            child: Container(
              width: double.infinity,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    const Color.fromARGB(
                      255,
                      240,
                      245,
                      240,
                    ), // Very light grey-green
                    const Color.fromARGB(
                      255,
                      235,
                      242,
                      235,
                    ), // Slightly darker light grey-green
                  ],
                ),
              ),
              child: SafeArea(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    const SizedBox(height: 32),
                    Text(
                      'Settings'.tr(),
                      style: Theme.of(
                        context,
                      ).textTheme.headlineMedium?.copyWith(
                        color: Theme.of(context).colorScheme.onPrimaryContainer,
                      ),
                    ),
                    const SizedBox(height: 32),

                    // Language Dropdown
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 24.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'choose_language'
                                .tr(), // <-- Add this to your translation files
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w600,
                              color:
                                  Theme.of(
                                    context,
                                  ).colorScheme.onPrimaryContainer,
                              shadows: [
                                Shadow(
                                  color: Colors.black.withOpacity(0.1),
                                  offset: const Offset(1, 1),
                                  blurRadius: 1,
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 8),
                          DropdownButton<Locale>(
                            value: currentLocale,
                            isExpanded: true,
                            onChanged: (Locale? newLocale) {
                              if (newLocale != null) {
                                context.setLocale(newLocale);
                              }
                            },
                            items: const [
                              DropdownMenuItem(
                                value: Locale('en'),
                                child: Text('English'),
                              ),
                              DropdownMenuItem(
                                value: Locale('hi'),
                                child: Text('हिन्दी'),
                              ),
                              DropdownMenuItem(
                                value: Locale('te'),
                                child: Text('తెలుగు'),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 32),

                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 24.0),
                      child: Container(
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.08),
                              blurRadius: 8,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: ElevatedButton(
                          onPressed:
                              state is SettingsLoading
                                  ? null
                                  : () {
                                    context.read<SettingsCubit>().logout();
                                  },
                          style: ElevatedButton.styleFrom(
                            minimumSize: const Size(double.infinity, 52),
                            backgroundColor: const Color.fromARGB(
                              255,
                              97,
                              156,
                              100,
                            ), // Darker, muted green
                            foregroundColor: Colors.white,
                            elevation: 0,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                            padding: const EdgeInsets.symmetric(vertical: 14),
                          ),
                          child:
                              state is SettingsLoading
                                  ? const SizedBox(
                                    height: 18,
                                    width: 18,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      valueColor: AlwaysStoppedAnimation<Color>(
                                        Colors.white,
                                      ),
                                    ),
                                  )
                                  : Row(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      const Icon(
                                        Icons.logout_rounded,
                                        size: 18,
                                        color: Colors.white,
                                      ),
                                      const SizedBox(width: 10),
                                      Text(
                                        'Logout'.tr(),
                                        style: const TextStyle(
                                          fontSize: 15,
                                          fontWeight: FontWeight.w500,
                                          color: Colors.white,
                                          letterSpacing: 0.3,
                                        ),
                                      ),
                                    ],
                                  ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
