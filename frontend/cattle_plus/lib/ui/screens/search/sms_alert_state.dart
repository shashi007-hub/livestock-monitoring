class Message {
  final int id;
  final String content;
  final String timestamp;

  Message({required this.id, required this.content, required this.timestamp});

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'],
      content: json['content'],
      timestamp: json['timestamp'],
    );
  }
}

abstract class MessageState {}

class MessageInitial extends MessageState {}

class MessageLoading extends MessageState {}

class MessageLoaded extends MessageState {
  final List<Message> messages;

  MessageLoaded({required this.messages});
}

class MessageError extends MessageState {
  final String errorMessage;

  MessageError(this.errorMessage);
}
