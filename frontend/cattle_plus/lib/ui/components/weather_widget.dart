import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:weather_icons/weather_icons.dart'; // Use weather_icons package
import 'package:intl/intl.dart'; // For date formatting if needed later
import '../../env.dart'; // Import your env.dart file for API key

class WeatherWidget extends StatefulWidget {
  final String username;
  final String city;

  const WeatherWidget({
    super.key,
    required this.username,
    required this.city,
  });

  @override
  State<WeatherWidget> createState() => _WeatherWidgetState();
}

class _WeatherWidgetState extends State<WeatherWidget> {
  Future<Map<String, dynamic>>? _weatherData;

  @override
  void initState() {
    super.initState();
    _fetchWeather();
  }

  Future<void> _fetchWeather() async {
    // IMPORTANT: Replace with your actual API key and endpoint
    
    final url = Uri.parse(
        'https://api.openweathermap.org/data/2.5/weather?q=${widget.city}&appid=$WEATHER_API_KEY&units=metric');

    setState(() {
      _weatherData = _fetchData(url);
    });
  }

  Future<Map<String, dynamic>> _fetchData(Uri url) async {
    try {
      final response = await http.get(url, headers: {
        'Content-Type': 'application/json',
      });
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        // Handle API errors (e.g., city not found, invalid key)
        print(response.body); // Log the response for debugging
        throw Exception('Failed to load weather data: ${response.toString()}');
      }
    } catch (e) {
      // Handle network errors or JSON parsing errors
      throw Exception('Failed to load weather data: $e');
    }
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) {
      return 'Good Morning';
    } else if (hour < 17) {
      return 'Good Afternoon';
    } else {
      return 'Good Evening';
    }
  }

  IconData _getWeatherIcon(String? iconCode) {
    // Map OpenWeatherMap icon codes to weather_icons
    // See: https://openweathermap.org/weather-conditions
    // And weather_icons mapping: https://github.com/fluttercommunity/weather_icons/blob/master/lib/src/weather_icons.dart (or check package docs)
    switch (iconCode) {
      // Day icons
      case '01d': return WeatherIcons.day_sunny;
      case '02d': return WeatherIcons.day_cloudy;
      case '03d': return WeatherIcons.cloud;
      case '04d': return WeatherIcons.cloudy;
      case '09d': return WeatherIcons.day_showers;
      case '10d': return WeatherIcons.day_rain;
      case '11d': return WeatherIcons.day_thunderstorm;
      case '13d': return WeatherIcons.day_snow;
      case '50d': return WeatherIcons.day_fog;

      // Night icons
      case '01n': return WeatherIcons.night_clear;
      case '02n': return WeatherIcons.night_alt_cloudy;
      case '03n': return WeatherIcons.cloud; // Often same as day for scattered
      case '04n': return WeatherIcons.cloudy; // Often same as day for broken
      case '09n': return WeatherIcons.night_alt_showers;
      case '10n': return WeatherIcons.night_alt_rain;
      case '11n': return WeatherIcons.night_alt_thunderstorm;
      case '13n': return WeatherIcons.night_alt_snow;
      case '50n': return WeatherIcons.night_fog;

      default: return WeatherIcons.na; // Default/unknown
    }
  }

  @override
  Widget build(BuildContext context) {
    final greeting = _getGreeting();

    return Card(
      margin: const EdgeInsets.all(16.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min, // Fit content
          children: [
            Text(
              '$greeting, ${widget.username}!',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            FutureBuilder<Map<String, dynamic>>(
              future: _weatherData,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: CircularProgressIndicator());
                } else if (snapshot.hasError) {
                  // Display more specific error if possible
                  return Center(child: Text('Error: ${snapshot.error}'));
                } else if (snapshot.hasData) {
                  final data = snapshot.data!;
                  final main = data['main'];
                  final weather = data['weather'][0];
                  final temp = main['temp']?.toDouble();
                  final description = weather['description'];
                  final iconCode = weather['icon'];
                  final cityName = data['name']; // City name from API

                  return Row(
                    children: [
                      Icon(_getWeatherIcon(iconCode), size: 40.0, color: Theme.of(context).iconTheme.color ?? Colors.black), // Use Icon
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              cityName ?? widget.city, // Show API city name or fallback
                              style: Theme.of(context).textTheme.titleLarge,
                            ),
                            Text(
                              '${temp?.toStringAsFixed(1) ?? '--'}°C, ${description ?? 'N/A'}',
                              style: Theme.of(context).textTheme.bodyMedium,
                            ),
                          ],
                        ),
                      ),
                    ],
                  );
                } else {
                  return const Center(child: Text('No weather data available.'));
                }
              },
            ),
          ],
        ),
      ),
    );
  }
}
