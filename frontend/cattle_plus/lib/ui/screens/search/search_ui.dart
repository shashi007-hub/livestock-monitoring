import 'package:flutter/material.dart';
import 'sms_alert_cubit.dart'; // Adjust path accordingly
import 'sms_alert_state.dart'; // Adjust path accordingly
import 'package:easy_localization/easy_localization.dart';

class SearchUI extends StatefulWidget {
  const SearchUI({super.key});

  @override
  _SearchUIState createState() => _SearchUIState();
}

class _SearchUIState extends State<SearchUI> {
  MessageState _state = MessageInitial();

  @override
  void initState() {
    super.initState();
    MessageCubit(this._updateState).fetchMessages();
  }

  void _updateState(MessageState state) {
    setState(() {
      _state = state;
    });
  }

  String _getRelativeTime(String timestamp) {
    final messageDate = DateTime.parse(timestamp);
    final currentDate = DateTime.now();
    final difference = currentDate.difference(messageDate);

    if (difference.inDays > 0) {
      return '${difference.inDays} ${difference.inDays > 1 ? 'days'.tr() : 'day'.tr()} ${'ago'.tr()}';
    } else if (difference.inHours > 0) {
      return '${difference.inHours} ${difference.inHours > 1 ? 'hours'.tr() : 'hour'.tr()} ${'ago'.tr()}';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes} ${difference.inMinutes > 1 ? 'minutes'.tr() : 'minute'.tr()} ${'ago'.tr()}';
    } else {
      return 'Just now'.tr();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Icon(
              Icons.notifications,
              color: const Color.fromARGB(255, 164, 5, 5),
            ),
            SizedBox(width: 8),
            Text(
              'sms_alert_history'.tr(),
              style: Theme.of(context).textTheme.headlineSmall,
            ),
          ],
        ),
      ),
      body: Builder(
        builder: (_) {
          if (_state is MessageLoading) {
            return Center(child: CircularProgressIndicator());
          } else if (_state is MessageError) {
            return Center(child: Text((_state as MessageError).errorMessage));
          } else if (_state is MessageLoaded) {
            final messages = (_state as MessageLoaded).messages;
            return ListView.builder(
              padding: const EdgeInsets.all(8.0),
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final message = messages[index];
                return MessageTile(
                  content: message.content,
                  timestamp: message.timestamp,
                  relativeTime: _getRelativeTime(message.timestamp),
                );
              },
            );
          }
          return Center(child: Text("No messages available"));
        },
      ),
    );
  }
}

class MessageTile extends StatelessWidget {
  final String content;
  final String timestamp;
  final String relativeTime;

  const MessageTile({
    Key? key,
    required this.content,
    required this.timestamp,
    required this.relativeTime,
  }) : super(key: key);

  String _formatTimestamp(String isoTimestamp) {
    final dateTime = DateTime.parse(isoTimestamp);
    return '${dateTime.year}-${_twoDigits(dateTime.month)}-${_twoDigits(dateTime.day)} '
        '${_twoDigits(dateTime.hour)}:${_twoDigits(dateTime.minute)}:${_twoDigits(dateTime.second)}';
  }

  String _twoDigits(int n) => n.toString().padLeft(2, '0');

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 16.0),
      child: Card(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        color: Colors.grey[200],
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                content,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                  color: Colors.black87,
                  height: 1.5,
                ),
              ),
              SizedBox(height: 8),
              Text(
                '${'Sent at'.tr()}: ${_formatTimestamp(timestamp)}',
                style: TextStyle(fontSize: 15, color: Colors.black38),
              ),
              SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.start,
                children: [
                  Icon(
                    Icons.access_time,
                    size: 18,
                    color: const Color.fromARGB(180, 182, 51, 51),
                  ),
                  SizedBox(width: 4),
                  Text(
                    relativeTime,
                    style: TextStyle(
                      fontSize: 12,
                      color: const Color.fromARGB(180, 182, 51, 51),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
