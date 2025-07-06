import 'package:cattle_plus/const.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:easy_localization/easy_localization.dart';
import 'dart:ui';
// Add intl package for date formatting

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
        return const Color.fromARGB(255, 69, 173, 73);
      case AnimalStatus.needsAttention:
        return const Color.fromARGB(255, 245, 175, 64); // Material Yellow 500
      case AnimalStatus.danger:
        return const Color.fromARGB(255, 245, 42, 42);
      // No default needed as all enum cases are handledR
    }
  }

  String _getStatusText(AnimalStatus status) {
    switch (status) {
      case AnimalStatus.normal:
        return 'Normal'.tr();
      case AnimalStatus.needsAttention:
        return 'Needs Attention'.tr();
      case AnimalStatus.danger:
        return 'Danger'.tr();
      // No default needed as all enum cases are handled
    }
  }

  IconData _getStatusIcon(AnimalStatus status) {
    switch (status) {
      case AnimalStatus.normal:
        return Icons.check_circle;
      case AnimalStatus.needsAttention:
        return Icons.warning;
      case AnimalStatus.danger:
        return Icons.error;
    }
  }

  @override
  Widget build(BuildContext context) {
    final statusColor = _getStatusColor(status);
    // final statusColor = Colors.pink.shade100;
    final statusText = _getStatusText(status);
    // final statusIcon = _getStatusIcon(status);
    final formattedLastSeen = DateFormat(
      'MMM d, yyyy hh:mm a',
    ).format(lastSeen);

    return InkWell(
      enableFeedback: true,
      onTap: onTap,
      child: Container(
        height: 150, // Adjust height as needed
        margin: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 16.0),
        decoration: BoxDecoration(borderRadius: BorderRadius.circular(12.0)),
        clipBehavior: Clip.antiAlias,
        child: Stack(
          children: [
            // Blurred background image
            Positioned.fill(child: Image.network(imageUrl, fit: BoxFit.cover)),
            Positioned.fill(
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 3, sigmaY: 3),
                child: Container(color: statusColor.withOpacity(0.5)),
              ),
            ),
            // Row with profile image on the left and text on the right
            Positioned.fill(
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Padding(
                    padding: const EdgeInsets.only(left: 20, right: 20),
                    child: Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(16),
                        image:
                            imageUrl.isNotEmpty
                                ? DecorationImage(
                                  image: NetworkImage(imageUrl),
                                  fit: BoxFit.cover,
                                )
                                : null,
                        color: Colors.white,
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.2),
                            blurRadius: 6,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child:
                          imageUrl.isEmpty
                              ? const Center(
                                child: Icon(
                                  Icons.pets,
                                  size: 40,
                                  color: Colors.grey,
                                ),
                              )
                              : null,
                    ),
                  ),
                  Expanded(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          name,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            shadows: [
                              Shadow(
                                blurRadius: 2.0,
                                color: Colors.black54,
                                offset: Offset(1, 1),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          tr('status_label', args: [statusText]),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            shadows: [
                              Shadow(
                                blurRadius: 1.0,
                                color: Colors.black54,
                                offset: Offset(1, 1),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          tr('last_update', args: [formattedLastSeen]),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 14,
                            shadows: [
                              Shadow(
                                blurRadius: 1.0,
                                color: Colors.black54,
                                offset: Offset(1, 1),
                              ),
                            ],
                          ),
                        ),
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
