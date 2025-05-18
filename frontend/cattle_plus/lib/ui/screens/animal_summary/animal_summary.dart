import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:fl_chart/fl_chart.dart';
import 'animal_summary_cubit.dart';
import 'package:easy_localization/easy_localization.dart';

final Map<String, String> problemKeyMap = {
  "High distress detected": "health.problem.high_distress_detected",
  "Abnormal vocalizations indicating distress":
      "health.problem.abnormal_vocalizations",
  "Increased heart rate": "health.problem.increased_heart_rate",
  "Lameness detected": "health.problem.lameness_detected",
  "Reduced mobility due to lameness": "health.problem.reduced_mobility",
};

final Map<String, String> solutionKeyMap = {
  "Check for environmental stressors or health issues":
      "health.solution.check_environmental_stressors",
  "Ensure adequate food and water are available":
      "health.solution.ensure_food_water",
  "Monitor for signs of illness": "health.solution.monitor_illness",
  "Inspect hooves and provide necessary treatment":
      "health.solution.inspect_hooves",
  "Provide rest and monitor for signs of improvement":
      "health.solution.provide_rest",
};

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
            'Animal Summary'.tr(),
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
                          imageUrl,
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
                  'Current Status'.tr(),
                  _getStatusWidget(context, animal.status),
                ),

                // Health Entries Section
                if (animal.status != AnimalStatus.allGood)
                  _buildSection(
                    context,
                    'Problems Identified'.tr(),
                    Table(
                      border: TableBorder.all(),
                      children:
                          animal.healthEntries.map((entry) {
                            final problemKey =
                                problemKeyMap[entry.problem] ?? entry.problem;
                            final solutionKey =
                                solutionKeyMap[entry.solution] ??
                                entry.solution;

                            return TableRow(
                              children: [
                                Padding(
                                  padding: const EdgeInsets.all(8.0),
                                  child: Center(child: Text(problemKey.tr())),
                                ),
                                Padding(
                                  padding: const EdgeInsets.all(8.0),
                                  child: Text(solutionKey.tr()),
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
                        'All Good! 🎉'.tr(),
                        style: Theme.of(context).textTheme.headlineMedium
                            ?.copyWith(color: Colors.green[800]),
                      ),
                    ),
                  ),

                // Feeding Analysis Graph Section
                const SizedBox(height: 24),
                _buildSection(
                  context,
                  'Feeding Analysis'.tr(),
                  _buildFeedingGraph(animal.feedingAnalysis),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFeedingGraph(List<FeedingAnalysis> feedingAnalysis) {
    if (feedingAnalysis.isEmpty) {
      return Center(
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Text(
            'No data recorded'.tr(),
            style: TextStyle(fontSize: 14, color: Colors.grey),
          ),
        ),
      );
    }

    final spots =
        feedingAnalysis
            .asMap()
            .entries
            .map(
              (entry) =>
                  FlSpot(entry.key.toDouble(), entry.value.avg.toDouble()),
            )
            .toList();

    final maxYValue = feedingAnalysis
        .map((e) => e.avg)
        .reduce((a, b) => a > b ? a : b);

    final maxYWithMargin = maxYValue + 0.2; // Add a small margin for spacing

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.only(bottom: 8.0),
          child: Text(
            'Year 2025',
            style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
          ),
        ),
        feedingAnalysis.isEmpty
            ? Center(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Text(
                  'No data recorded'.tr(),
                  style: TextStyle(fontSize: 14, color: Colors.grey),
                ),
              ),
            )
            : SizedBox(
              height: 300,
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(
                    show: true,
                    drawVerticalLine: true,
                    verticalInterval: 1,
                    horizontalInterval: 1,
                    getDrawingHorizontalLine:
                        (value) =>
                            FlLine(color: Colors.grey[300]!, strokeWidth: 1),
                    getDrawingVerticalLine:
                        (value) =>
                            FlLine(color: Colors.grey[300]!, strokeWidth: 1),
                  ),
                  titlesData: FlTitlesData(
                    topTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    rightTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        interval: 1,
                        getTitlesWidget: (value, meta) {
                          if (value > maxYValue)
                            return const SizedBox.shrink(); // Hide labels beyond maxY
                          return Text(
                            '${value.toStringAsFixed(1)}h',
                            style: const TextStyle(fontSize: 10),
                          );
                        },
                      ),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        interval: 1,
                        getTitlesWidget: (value, meta) {
                          final index = value.toInt();
                          if (index >= 0 && index < feedingAnalysis.length) {
                            final date = feedingAnalysis[index].date;
                            final shortDate = date.substring(5);

                            return Padding(
                              padding: const EdgeInsets.only(top: 4.0),
                              child: Text(
                                shortDate,
                                style: const TextStyle(fontSize: 10),
                              ),
                            );
                          }
                          return const Text('');
                        },
                      ),
                    ),
                  ),
                  borderData: FlBorderData(
                    show: true,
                    border: Border.all(color: Colors.grey[300]!, width: 1),
                  ),
                  lineBarsData: [
                    LineChartBarData(
                      spots: spots,
                      isCurved: true,
                      gradient: LinearGradient(
                        colors: [Colors.blue, Colors.lightBlueAccent],
                      ),
                      barWidth: 4,
                      belowBarData: BarAreaData(
                        show: true,
                        gradient: LinearGradient(
                          colors: [
                            Colors.blue.withOpacity(0.3),
                            Colors.lightBlueAccent.withOpacity(0.1),
                          ],
                        ),
                      ),
                    ),
                  ],
                  minX: 0,
                  maxX: (feedingAnalysis.length - 1).toDouble(),
                  minY: 0,
                  maxY: maxYWithMargin, // Add margin to maxY for spacing
                ),
              ),
            ),
      ],
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
        text = 'Needs Immediate Attention'.tr();
        icon = Icons.error;
        break;
      case AnimalStatus.needsAttention:
        color = Colors.orange;
        text = 'Needs Attention'.tr();
        icon = Icons.warning;
        break;
      case AnimalStatus.allGood:
        color = Colors.green;
        text = 'All Good'.tr();
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
