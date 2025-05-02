import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'sms_alert_state.dart';
import 'package:cattle_plus/env.dart';

class MessageCubit {
  final Function updateState;

  MessageCubit(this.updateState);

  Future<void> fetchMessages() async {
    updateState(MessageLoading());
    try {
      final userId = 2;
      final response = await http.get(
        Uri.parse('http://$SERVER_URL/users/$userId/smsalerts'),
      );
      // Simulating the response as a JSON string
      print(response.body);
      final responsebody = json.encode({
        "messages": [
          {
            "id": 1,
            "content": "Test message 1",
            "timestamp": "2025-05-01 12:46:34",
          },
          {
            "id": 2,
            "content": "Test message 2",
            "timestamp": "2025-05-01 12:46:34",
          },
        ],
      });

      final responsecode = response.statusCode;

      if (responsecode == 200) {
        // Decode the JSON string into a Map
        final Map<String, dynamic> decodedResponse = json.decode(response.body);

        // Access the 'messages' field, which is a list
        List messages = List.from(decodedResponse['messages']);

        updateState(
          MessageLoaded(
            messages:
                messages.map((message) => Message.fromJson(message)).toList(),
          ),
        );
      } else {
        updateState(MessageError("Failed to load messages"));
      }
    } catch (e) {
      updateState(MessageError("Error fetching messages: $e"));
    }
  }
}
