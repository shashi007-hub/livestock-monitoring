import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'animal_summary_cubit.dart';

class AnimalSummaryScreen extends StatelessWidget {
  final String bovineId;

  const AnimalSummaryScreen({super.key, required this.bovineId});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => AnimalSummaryCubit()..fetchAnimalDetails(bovineId),
      child: Scaffold(
        appBar: AppBar(
          title: Text(
            'Animal Summary',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
        ),
        body: BlocBuilder<AnimalSummaryCubit, AnimalSummaryState>(
          builder: (context, state) {
            if (state is AnimalSummaryLoading) {
              return const Center(child: CircularProgressIndicator());
            } else if (state is AnimalSummaryError) {
              return Center(
                child: Text(
                  state.message,
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
              );
            } else if (state is AnimalSummaryLoaded) {
              return _buildSummaryContent(context, state.animal);
            }
            return const SizedBox.shrink();
          },
        ),
      ),
    );
  }

  Widget _buildSummaryContent(BuildContext context, AnimalDetails animal) {
    // Use the `getBovineImageUrl` function to get the image URL
    final imageUrl = getBovineImageUrl(int.parse(animal.id));

    return SafeArea(
      child: Container(
        decoration: BoxDecoration(color: _getBackgroundColor(animal.status)),
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Animal Image and Name
                Center(
                  child: Column(
                    children: [
                      Container(
                        height: 200,
                        width: 200,
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(12),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.2),
                              blurRadius: 8,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        clipBehavior: Clip.antiAlias,
                        child: Image.network(
                          imageUrl, // Use the URL from `getBovineImageUrl`
                          fit: BoxFit.cover,
                          loadingBuilder: (context, child, loadingProgress) {
                            if (loadingProgress == null) return child;
                            return Center(
                              child: CircularProgressIndicator(
                                value:
                                    loadingProgress.expectedTotalBytes != null
                                        ? loadingProgress
                                                .cumulativeBytesLoaded /
                                            loadingProgress.expectedTotalBytes!
                                        : null,
                              ),
                            );
                          },
                          errorBuilder: (context, error, stackTrace) {
                            return Container(
                              color: Colors.grey[200],
                              child: const Icon(
                                Icons.error_outline,
                                size: 40,
                                color: Colors.red,
                              ),
                            );
                          },
                        ),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        animal.name,
                        style: Theme.of(context).textTheme.headlineMedium,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Status Section
                _buildSection(
                  context,
                  'Current Status',
                  _getStatusWidget(context, animal.status),
                ),

                // Health Entries Section
                if (animal.status != AnimalStatus.allGood)
                  _buildSection(
                    context,
                    'Problems Identified',
                    Table(
                      border: TableBorder.all(),
                      children:
                          animal.healthEntries.map((entry) {
                            return TableRow(
                              children: [
                                Padding(
                                  padding: const EdgeInsets.all(8.0),
                                  child: Center(child: Text(entry.problem)),
                                ),
                                Padding(
                                  padding: const EdgeInsets.all(8.0),
                                  child: Text(entry.solution),
                                ),
                              ],
                            );
                          }).toList(),
                    ),
                  ),

                // All Good Message
                if (animal.status == AnimalStatus.allGood)
                  Center(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 24.0),
                      child: Text(
                        'All Good! 🎉',
                        style: Theme.of(context).textTheme.headlineMedium
                            ?.copyWith(color: Colors.green[800]),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Color _getBackgroundColor(AnimalStatus status) {
    switch (status) {
      case AnimalStatus.needsImmediateAttention:
        return Colors.red[100]!;
      case AnimalStatus.needsAttention:
        return Colors.yellow[100]!;
      case AnimalStatus.allGood:
        return Colors.green[100]!;
    }
  }

  Widget _buildSection(BuildContext context, String title, Widget content) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 8),
          content,
          const SizedBox(height: 8),
          const Divider(),
        ],
      ),
    );
  }

  Widget _getStatusWidget(BuildContext context, AnimalStatus status) {
    Color color;
    String text;
    IconData icon;

    switch (status) {
      case AnimalStatus.needsImmediateAttention:
        color = Colors.red;
        text = 'Needs Immediate Attention';
        icon = Icons.error;
        break;
      case AnimalStatus.needsAttention:
        color = Colors.orange;
        text = 'Needs Attention';
        icon = Icons.warning;
        break;
      case AnimalStatus.allGood:
        color = Colors.green;
        text = 'All Good';
        icon = Icons.check_circle;
        break;
    }

    return Row(
      children: [
        Icon(icon, color: color),
        const SizedBox(width: 8),
        Text(
          text,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            color: color,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
}
