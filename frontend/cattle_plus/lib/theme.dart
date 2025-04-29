import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

// Define semantic font sizes
const double headlineLargeSize = 32.0;
const double headlineMediumSize = 28.0;
const double headlineSmallSize = 24.0;
const double titleLargeSize = 22.0;
const double titleMediumSize = 16.0;
const double titleSmallSize = 14.0;
const double bodyLargeSize = 16.0;
const double bodyMediumSize = 14.0;
const double bodySmallSize = 12.0;
const double labelLargeSize = 14.0;
const double labelMediumSize = 12.0;
const double labelSmallSize = 11.0;

// Define the global theme
final ThemeData appTheme = ThemeData(
  useMaterial3: true, // Recommended for new Flutter projects
  colorScheme: ColorScheme.fromSeed(
    seedColor: Colors.green, // Example seed color
    brightness: Brightness.light,
  ),
  textTheme: TextTheme(
    // Display styles (rarely used)
    // displayLarge: GoogleFonts.roboto(fontSize: 57.0, fontWeight: FontWeight.w400),
    // displayMedium: GoogleFonts.roboto(fontSize: 45.0, fontWeight: FontWeight.w400),
    // displaySmall: GoogleFonts.roboto(fontSize: 36.0, fontWeight: FontWeight.w400),

    // Headline styles
    headlineLarge: GoogleFonts.lato(fontSize: headlineLargeSize, fontWeight: FontWeight.bold),
    headlineMedium: GoogleFonts.lato(fontSize: headlineMediumSize, fontWeight: FontWeight.bold),
    headlineSmall: GoogleFonts.lato(fontSize: headlineSmallSize, fontWeight: FontWeight.bold),

    // Title styles
    titleLarge: GoogleFonts.openSans(fontSize: titleLargeSize, fontWeight: FontWeight.w600),
    titleMedium: GoogleFonts.openSans(fontSize: titleMediumSize, fontWeight: FontWeight.w600),
    titleSmall: GoogleFonts.openSans(fontSize: titleSmallSize, fontWeight: FontWeight.w600),

    // Body styles
    bodyLarge: GoogleFonts.roboto(fontSize: bodyLargeSize, fontWeight: FontWeight.normal),
    bodyMedium: GoogleFonts.roboto(fontSize: bodyMediumSize, fontWeight: FontWeight.normal), // Default text style
    bodySmall: GoogleFonts.roboto(fontSize: bodySmallSize, fontWeight: FontWeight.normal),

    // Label styles (for buttons, captions, etc.)
    labelLarge: GoogleFonts.roboto(fontSize: labelLargeSize, fontWeight: FontWeight.w500), // Button text style
    labelMedium: GoogleFonts.roboto(fontSize: labelMediumSize, fontWeight: FontWeight.w500),
    labelSmall: GoogleFonts.roboto(fontSize: labelSmallSize, fontWeight: FontWeight.w500),
  ),
  // You can customize other theme properties here, like:
  // appBarTheme: AppBarTheme(...)
  // buttonTheme: ButtonThemeData(...)
  // inputDecorationTheme: InputDecorationTheme(...)
);

// Example of using a specific text style:
// Text('Hello', style: Theme.of(context).textTheme.headlineMedium)
