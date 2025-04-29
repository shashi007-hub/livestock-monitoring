import 'package:cattle_plus/const.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart'; // Add intl package for date formatting


class AnimalTile extends StatelessWidget {
  final String name;
  final AnimalStatus status;
  final DateTime lastSeen;
  final String imageUrl;
  final VoidCallback onTap; 

  const AnimalTile({
    super.key,
    required this.name,
    required this.status,
    required this.lastSeen,
    required this.imageUrl,
    required this.onTap,
  });

  Color _getStatusColor(AnimalStatus status) {
    switch (status) {
      case AnimalStatus.normal:
        return Colors.green.withOpacity(0.7);
      case AnimalStatus.needsAttention:
        return Colors.orange.withOpacity(0.7);
      case AnimalStatus.danger:
        return Colors.red.withOpacity(0.7);
      // No default needed as all enum cases are handled
    }
  }

  String _getStatusText(AnimalStatus status) {
    switch (status) {
      case AnimalStatus.normal:
        return 'Normal';
      case AnimalStatus.needsAttention:
        return 'Needs Attention';
      case AnimalStatus.danger:
        return 'Danger';
       // No default needed as all enum cases are handled
    }
  }

  @override
  Widget build(BuildContext context) {
    final statusColor = _getStatusColor(status);
    final statusText = _getStatusText(status);
    final formattedLastSeen = DateFormat('MMM d, yyyy hh:mm a').format(lastSeen);

    return InkWell(
      enableFeedback: true,
      onTap : onTap,
      child : Container(
        height: 150, // Adjust height as needed
        margin: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 16.0),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12.0),
          image: DecorationImage(
            image: NetworkImage(imageUrl),
            fit: BoxFit.cover,
            colorFilter: ColorFilter.mode(
              Colors.black.withOpacity(0.4), // Adjust opacity for translucency
              BlendMode.darken,
            ),
          ),
        ),
        child: Row(
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(10),
                image: imageUrl != null
                    ? DecorationImage(
                        image: NetworkImage(imageUrl),
                        fit: BoxFit.cover,
                      )
                    : null,
              ),
              child: imageUrl == null
                  ? const Center(
                      child: Icon(Icons.pets, size: 40, color: Colors.grey),
                    )
                  : null,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    name,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      shadows: [
                        Shadow(blurRadius: 2.0, color: Colors.black54, offset: Offset(1, 1))
                      ],
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Status: $statusText',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.9),
                      fontSize: 16,
                       shadows: const [
                        Shadow(blurRadius: 1.0, color: Colors.black54, offset: Offset(1, 1))
                      ],
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Last Update: $formattedLastSeen',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.8),
                      fontSize: 14,
                       shadows: const [
                        Shadow(blurRadius: 1.0, color: Colors.black54, offset: Offset(1, 1))
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}