import 'package:flutter/material.dart';

class SearchUI extends StatelessWidget {
  const SearchUI({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('SMS Alert History', style: Theme.of(context).textTheme.headlineSmall),
      ),
    );
  }
}