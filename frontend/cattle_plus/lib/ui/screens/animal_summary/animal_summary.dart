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
          elevation: 8,
          shadowColor: Colors.black26,
          backgroundColor: Colors.white,
          surfaceTintColor: Colors.transparent,
          title: Text(
            'Animal Summary'.tr(),
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              color: Colors.black87,
              fontWeight: FontWeight.w600,
            ),
          ),
          iconTheme: const IconThemeData(color: Colors.black87),
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
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.3),
                              blurRadius: 15,
                              offset: const Offset(0, 8),
                              spreadRadius: 2,
                            ),
                            BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 30,
                              offset: const Offset(0, 15),
                              spreadRadius: 5,
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
                  Card(
                    elevation: 4,
                    margin: const EdgeInsets.symmetric(vertical: 8.0),
                    color: Colors.white,
                    child: Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: _buildSection(
                        context,
                        'Problems Identified'.tr(),
                        Padding(
                          padding: const EdgeInsets.only(top: 8.0),
                          child: Container(
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(
                                color: Colors.grey[200]!,
                                width: 1,
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.grey[100]!,
                                  blurRadius: 4,
                                  offset: const Offset(0, 2),
                                ),
                              ],
                            ),
                            child: Table(
                              border: TableBorder(
                                horizontalInside: BorderSide(
                                  color: Colors.grey[100]!,
                                  width: 1,
                                ),
                              ),
                              columnWidths: const {
                                0: FlexColumnWidth(1.5),
                                1: FlexColumnWidth(2.0),
                              },
                              children: [
                                // Header Row
                                TableRow(
                                  decoration: BoxDecoration(
                                    color: Colors.grey[50],
                                    borderRadius: const BorderRadius.only(
                                      topLeft: Radius.circular(12),
                                      topRight: Radius.circular(12),
                                    ),
                                  ),
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 16.0,
                                        vertical: 12.0,
                                      ),
                                      child: Text(
                                        'Symptom'.tr(),
                                        style: const TextStyle(
                                          fontWeight: FontWeight.w900,
                                          fontSize: 16,
                                          color: Colors.black54,
                                        ),
                                        textAlign: TextAlign.center,
                                      ),
                                    ),
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 16.0,
                                        vertical: 12.0,
                                      ),
                                      child: Text(
                                        'Treatment'.tr(),
                                        style: const TextStyle(
                                          fontWeight: FontWeight.w900,
                                          fontSize: 16,
                                          color: Colors.black54,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                                // Data Rows
                                ...animal.healthEntries.map((entry) {
                                  final problemKey =
                                      problemKeyMap[entry.problem] ??
                                      entry.problem;
                                  final solutionKey =
                                      solutionKeyMap[entry.solution] ??
                                      entry.solution;

                                  return TableRow(
                                    decoration: const BoxDecoration(
                                      color: Colors.white,
                                    ),
                                    children: [
                                      Container(
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 16.0,
                                          vertical: 12.0,
                                        ),
                                        child: Text(
                                          problemKey.tr(),
                                          style: TextStyle(
                                            fontSize: 15,
                                            color: Colors.red[400],
                                            fontWeight: FontWeight.bold,
                                            height: 1.4,
                                          ),
                                          textAlign: TextAlign.left,
                                        ),
                                      ),
                                      Container(
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 16.0,
                                          vertical: 12.0,
                                        ),
                                        child: Text(
                                          solutionKey.tr(),
                                          style: const TextStyle(
                                            fontSize: 15,
                                            color: Colors.black54,
                                            fontWeight: FontWeight.w600,
                                            height: 1.4,
                                          ),
                                        ),
                                      ),
                                    ],
                                  );
                                }).toList(),
                              ],
                            ),
                          ),
                        ),
                      ),
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
                Card(
                  elevation: 4,
                  margin: const EdgeInsets.symmetric(vertical: 8.0),
                  color: Colors.white,
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: _buildSection(
                      context,
                      'Feeding Analysis'.tr(),
                      _buildFeedingGraph(animal.feedingAnalysis),
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

  Widget _buildFeedingGraph(List<FeedingAnalysis> feedingAnalysis) {
    if (feedingAnalysis.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              Icon(Icons.bar_chart_outlined, size: 48, color: Colors.grey[400]),
              const SizedBox(height: 8),
              Text(
                'No grazing data recorded'.tr(),
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey[600],
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'Grazing time data will appear here'.tr(),
                style: TextStyle(fontSize: 14, color: Colors.grey[500]),
              ),
            ],
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

    final minYValue = feedingAnalysis
        .map((e) => e.avg)
        .reduce((a, b) => a < b ? a : b);

    final maxYWithMargin = maxYValue + (maxYValue * 0.1); // 10% margin
    final minYWithMargin = (minYValue - (minYValue * 0.1)).clamp(
      0.0,
      double.infinity,
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header with summary
        Container(
          padding: const EdgeInsets.all(16.0),
          decoration: BoxDecoration(
            color: Colors.blue[50],
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.blue[200]!, width: 1),
          ),
          child: Row(
            children: [
              Icon(Icons.timeline, color: Colors.blue[600], size: 24),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Average Grazing Time'.tr(),
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.black87,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      // '${feedingAnalysis.length} days recorded'.tr(),
                      tr(
                        'days_recorded',
                        args: [feedingAnalysis.length.toString()],
                      ),
                      style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                    ),
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    '${maxYValue.toStringAsFixed(1)} ${tr('h')}',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.blue[600],
                    ),
                  ),
                  Text(
                    'Peak grazing time'.tr(),
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Chart
        Container(
          height: 280,
          padding: const EdgeInsets.all(16.0),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.grey[200]!, width: 1),
            boxShadow: [
              BoxShadow(
                color: Colors.grey[200]!,
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: LineChart(
            LineChartData(
              gridData: FlGridData(
                show: true,
                drawVerticalLine: true,
                verticalInterval: 1,
                horizontalInterval: 1,
                getDrawingHorizontalLine:
                    (value) => FlLine(color: Colors.grey[200]!, strokeWidth: 1),
                getDrawingVerticalLine:
                    (value) => FlLine(color: Colors.grey[200]!, strokeWidth: 1),
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
                    reservedSize: 40,
                    getTitlesWidget: (value, meta) {
                      if (value > maxYValue) return const SizedBox.shrink();
                      return Padding(
                        padding: const EdgeInsets.only(right: 8.0),
                        child: Text(
                          '${value.toStringAsFixed(1)}${tr('h')}',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                            color: Colors.grey[700],
                          ),
                        ),
                      );
                    },
                  ),
                ),
                bottomTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    interval: 1,
                    reservedSize: 30,
                    getTitlesWidget: (value, meta) {
                      final index = value.toInt();
                      if (index >= 0 && index < feedingAnalysis.length) {
                        final date = feedingAnalysis[index].date;
                        final shortDate = date.substring(5); // Remove year
                        return Padding(
                          padding: const EdgeInsets.only(top: 8.0),
                          child: Text(
                            shortDate,
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w500,
                              color: Colors.grey[600],
                            ),
                          ),
                        );
                      }
                      return const SizedBox.shrink();
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
                    colors: [Colors.blue[400]!, Colors.blue[600]!],
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                  ),
                  barWidth: 3,
                  dotData: FlDotData(
                    show: true,
                    getDotPainter: (spot, percent, barData, index) {
                      return FlDotCirclePainter(
                        radius: 4,
                        color: Colors.blue[600]!,
                        strokeWidth: 2,
                        strokeColor: Colors.white,
                      );
                    },
                  ),
                  belowBarData: BarAreaData(
                    show: true,
                    gradient: LinearGradient(
                      colors: [
                        Colors.blue[400]!.withOpacity(0.3),
                        Colors.blue[600]!.withOpacity(0.1),
                      ],
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                    ),
                  ),
                ),
              ],
              minX: 0,
              maxX: (feedingAnalysis.length - 1).toDouble(),
              minY: minYWithMargin,
              maxY: maxYWithMargin,
            ),
          ),
        ),

        // Legend
        const SizedBox(height: 12),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                color: Colors.blue[600],
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 8),
            Text(
              'Daily Grazing Time (Hours)'.tr(),
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: Colors.grey[700],
              ),
            ),
          ],
        ),
      ],
    );
  }

  Color _getBackgroundColor(AnimalStatus status) {
    switch (status) {
      case AnimalStatus.needsImmediateAttention:
        return const Color.fromARGB(255, 255, 245, 245)!;
      case AnimalStatus.needsAttention:
        return const Color.fromARGB(255, 244, 238, 208)!;
      case AnimalStatus.allGood:
        return const Color.fromARGB(255, 226, 247, 227)!;
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
        color = const Color.fromARGB(255, 226, 45, 32);
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
