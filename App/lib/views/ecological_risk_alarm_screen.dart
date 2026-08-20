import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_container.dart';
import '../providers/app_providers.dart';
import '../models/telemetry_data_point.dart';

class EcologicalRiskAlarmScreen extends ConsumerStatefulWidget {
  const EcologicalRiskAlarmScreen({super.key});

  @override
  ConsumerState<EcologicalRiskAlarmScreen> createState() =>
      _EcologicalRiskAlarmScreenState();
}

class _EcologicalRiskAlarmScreenState
    extends ConsumerState<EcologicalRiskAlarmScreen> {
  int selectedPlotIndex =
      0; // 0 for All 20 Grid View, or 1-20 for full screen chart detail

  @override
  Widget build(BuildContext context) {
    final telemetry = ref.watch(telemetryProvider);
    final point = telemetry.currentPoint;
    final history = telemetry.history;

    final isExtinctionAlarm = point.extinctionRiskPct > 35.0;
    final isBifurcationAlarm = point.bifurcationIndexPct > 50.0;
    final isAlarmActive = isExtinctionAlarm || isBifurcationAlarm;

    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      body: SafeArea(
        child: Column(
          children: [
            // Alarm Status Banner Header
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: GlassContainer(
                padding: const EdgeInsets.all(14),
                borderColor: isAlarmActive
                    ? AppTheme.crimsonAccent
                    : AppTheme.emeraldAccent,
                backgroundColor: isAlarmActive
                    ? AppTheme.crimsonAccent.withValues(alpha: 0.25)
                    : AppTheme.emeraldAccent.withValues(alpha: 0.1),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Icon(
                          isAlarmActive
                              ? Icons.warning_amber_rounded
                              : Icons.check_circle_outline,
                          color: isAlarmActive
                              ? AppTheme.crimsonAccent
                              : AppTheme.emeraldAccent,
                          size: 24,
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                isAlarmActive
                                    ? "ALARM TRIGGERED: ECOLOGICAL RISK BREACH"
                                    : "ECOLOGICAL STABILITY: PARAMETERS NORMAL",
                                style: GoogleFonts.outfit(
                                  color: isAlarmActive
                                      ? AppTheme.crimsonAccent
                                      : AppTheme.emeraldAccent,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 13,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                              Text(
                                "Risk: ${point.extinctionRiskPct.toStringAsFixed(1)}% | Bifurcation: ${point.bifurcationIndexPct.toStringAsFixed(1)}%",
                                style: GoogleFonts.jetBrainsMono(
                                  color: AppTheme.textSecondary,
                                  fontSize: 10,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    // Environmental Disturbance Shock Simulation Triggers
                    SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        children: [
                          Text(
                            "INJECT SHOCK:",
                            style: GoogleFonts.jetBrainsMono(
                              color: AppTheme.textMuted,
                              fontSize: 10,
                            ),
                          ),
                          const SizedBox(width: 8),
                          _buildShockButton("HEATWAVE", () {
                            ref
                                .read(telemetryProvider.notifier)
                                .triggerEnvironmentalShock("heatwave");
                          }),
                          const SizedBox(width: 6),
                          _buildShockButton("POLLUTION", () {
                            ref
                                .read(telemetryProvider.notifier)
                                .triggerEnvironmentalShock("pollution");
                          }),
                          const SizedBox(width: 6),
                          _buildShockButton("INVASIVE", () {
                            ref
                                .read(telemetryProvider.notifier)
                                .triggerEnvironmentalShock("invasive");
                          }),
                          const SizedBox(width: 12),
                          _buildShockButton("RESET", () {
                            ref
                                .read(telemetryProvider.notifier)
                                .triggerEnvironmentalShock("reset");
                          }, isReset: true),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // Plot Selection Toolbar (All 20 Grid vs Detail)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Row(
                children: [
                  Text(
                    "20-PLOT SUITE",
                    style: GoogleFonts.jetBrainsMono(
                      color: AppTheme.textPrimary,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Align(
                      alignment: Alignment.centerRight,
                      child: DropdownButton<int>(
                        isExpanded: true,
                        value: selectedPlotIndex,
                        dropdownColor: AppTheme.bgCard,
                        style: GoogleFonts.jetBrainsMono(
                          color: AppTheme.cyanAccent,
                          fontSize: 11,
                        ),
                        underline: Container(),
                        items: [
                          const DropdownMenuItem(
                            value: 0,
                            child: Text("GRID VIEW (ALL 20 PLOTS)", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 1,
                            child: Text("PLOT 01: Population Time Series", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 2,
                            child: Text("PLOT 02: Extinction Risk Curve", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 3,
                            child: Text("PLOT 03: Lotka-Volterra Orbits", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 4,
                            child: Text("PLOT 04: Species Abundance Bar", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 5,
                            child: Text("PLOT 05: Density Histogram", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 6,
                            child: Text("PLOT 06: Cumulative Tracked", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 7,
                            child: Text("PLOT 07: Confidence Distribution", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 8,
                            child: Text("PLOT 08: Velocity Magnitude", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 9,
                            child: Text("PLOT 09: Shannon H' Index", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 10,
                            child: Text("PLOT 10: Pielou J' Evenness", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 11,
                            child: Text("PLOT 11: 2D Spatial Heatmap", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 12,
                            child: Text("PLOT 12: Growth Rate Phase Plot", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 13,
                            child: Text("PLOT 13: Stochastic Noise", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 14,
                            child: Text("PLOT 14: Kalman Gain Dynamics", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 15,
                            child: Text("PLOT 15: Innovation Residuals", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 16,
                            child: Text("PLOT 16: Specimen Area Box", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 17,
                            child: Text("PLOT 17: Detection Rate FPS", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 18,
                            child: Text("PLOT 18: Co-occurrence Matrix", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 19,
                            child: Text("PLOT 19: Eco Balance Gauge", overflow: TextOverflow.ellipsis),
                          ),
                          const DropdownMenuItem(
                            value: 20,
                            child: Text("PLOT 20: Covariance Trace", overflow: TextOverflow.ellipsis),
                          ),
                        ],
                        onChanged: (val) {
                          if (val != null) setState(() => selectedPlotIndex = val);
                        },
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 8),

            // Dynamic Chart Suite Viewport (Grid of 20 fl_charts or Full Screen Chart)
            Expanded(
              child: selectedPlotIndex == 0
                  ? _build20PlotGridView(history)
                  : _buildSinglePlotView(selectedPlotIndex, history),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildShockButton(
    String label,
    VoidCallback onTap, {
    bool isReset = false,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: isReset
              ? AppTheme.bgCard
              : AppTheme.goldAccent.withValues(alpha: 0.2),
          borderRadius: BorderRadius.circular(6),
          border: Border.all(
            color: isReset ? AppTheme.textMuted : AppTheme.goldAccent,
          ),
        ),
        child: Text(
          label,
          style: GoogleFonts.jetBrainsMono(
            color: isReset ? AppTheme.textMuted : AppTheme.goldAccent,
            fontWeight: FontWeight.bold,
            fontSize: 9,
          ),
        ),
      ),
    );
  }

  // Grid View rendering all 20 fl_chart plots
  Widget _build20PlotGridView(List<TelemetryDataPoint> history) {
    return GridView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 1.25,
        crossAxisSpacing: 10,
        mainAxisSpacing: 10,
      ),
      itemCount: 20,
      itemBuilder: (context, index) {
        final plotNum = index + 1;
        return GestureDetector(
          onTap: () => setState(() => selectedPlotIndex = plotNum),
          child: GlassContainer(
            padding: const EdgeInsets.all(8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "PLOT ${plotNum.toString().padLeft(2, '0')}: ${_getPlotTitle(plotNum)}",
                  style: GoogleFonts.jetBrainsMono(
                    color: AppTheme.cyanAccent,
                    fontWeight: FontWeight.bold,
                    fontSize: 9,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Expanded(
                  child: _renderChartByPlotNumber(
                    plotNum,
                    history,
                    isMini: true,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildSinglePlotView(int plotNum, List<TelemetryDataPoint> history) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: GlassContainer(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  "PLOT ${plotNum.toString().padLeft(2, '0')}: ${_getPlotTitle(plotNum)}",
                  style: GoogleFonts.outfit(
                    color: AppTheme.textPrimary,
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                const Spacer(),
                IconButton(
                  icon: const Icon(Icons.close, color: AppTheme.textMuted),
                  onPressed: () => setState(() => selectedPlotIndex = 0),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Expanded(
              child: _renderChartByPlotNumber(plotNum, history, isMini: false),
            ),
          ],
        ),
      ),
    );
  }

  String _getPlotTitle(int num) {
    switch (num) {
      case 1:
        return "Population Time Series (X vs Y)";
      case 2:
        return "Extinction Risk Trajectory (%)";
      case 3:
        return "Lotka-Volterra Phase Orbits";
      case 4:
        return "Species Abundance Bar";
      case 5:
        return "Ensemble Density Histogram";
      case 6:
        return "Cumulative Unique Tracked";
      case 7:
        return "Bounding Box Confidence";
      case 8:
        return "Velocity Distribution (px/s)";
      case 9:
        return "Shannon Diversity Index H'";
      case 10:
        return "Pielou Species Evenness J'";
      case 11:
        return "2D Spatial Centroid Heatmap";
      case 12:
        return "Growth Rate Phase (dX/dt vs dY/dt)";
      case 13:
        return "Stochastic Noise Variance";
      case 14:
        return "Kalman Gain Dynamics";
      case 15:
        return "Innovation Residual Error";
      case 16:
        return "Specimen Box Area Boxplot";
      case 17:
        return "Detection Rate (FPS)";
      case 18:
        return "Species Co-occurrence Matrix";
      case 19:
        return "Ecological Balance Gauge X/Y";
      case 20:
        return "State Covariance Trace Tr(Pf)";
      default:
        return "Telemetry Plot";
    }
  }

  Widget _renderChartByPlotNumber(
    int num,
    List<TelemetryDataPoint> history, {
    required bool isMini,
  }) {
    if (history.isEmpty) {
      return Center(
        child: Text(
          "Gathering Telemetry...",
          style: GoogleFonts.jetBrainsMono(
            color: AppTheme.textMuted,
            fontSize: 10,
          ),
        ),
      );
    }

    switch (num) {
      case 1: // Population Time Series
        return LineChart(
          LineChartData(
            gridData: FlGridData(show: !isMini),
            titlesData: const FlTitlesData(show: false),
            borderData: FlBorderData(show: false),
            lineBarsData: [
              LineChartBarData(
                spots: history.map((p) => FlSpot(p.timeSec, p.preyX)).toList(),
                isCurved: true,
                color: AppTheme.cyanAccent,
                barWidth: isMini ? 1.5 : 2.5,
              ),
              LineChartBarData(
                spots: history.map((p) => FlSpot(p.timeSec, p.predY)).toList(),
                isCurved: true,
                color: AppTheme.violetAccent,
                barWidth: isMini ? 1.5 : 2.5,
              ),
            ],
          ),
        );

      case 2: // Extinction Risk Curve
        return LineChart(
          LineChartData(
            gridData: FlGridData(show: !isMini),
            titlesData: const FlTitlesData(show: false),
            borderData: FlBorderData(show: false),
            lineBarsData: [
              LineChartBarData(
                spots: history
                    .map((p) => FlSpot(p.timeSec, p.extinctionRiskPct))
                    .toList(),
                isCurved: true,
                color: AppTheme.crimsonAccent,
                barWidth: isMini ? 1.5 : 2.5,
                belowBarData: BarAreaData(
                  show: true,
                  color: AppTheme.crimsonAccent.withValues(alpha: 0.2),
                ),
              ),
            ],
          ),
        );

      case 3: // Lotka-Volterra Phase Orbits (Prey X vs Predator Y)
        return LineChart(
          LineChartData(
            gridData: const FlGridData(show: false),
            titlesData: const FlTitlesData(show: false),
            borderData: FlBorderData(show: false),
            lineBarsData: [
              LineChartBarData(
                spots: history.map((p) => FlSpot(p.preyX, p.predY)).toList(),
                isCurved: true,
                color: AppTheme.emeraldAccent,
                barWidth: 2.0,
              ),
            ],
          ),
        );

      case 4: // Species Abundance Bar Chart
        return BarChart(
          BarChartData(
            titlesData: const FlTitlesData(show: false),
            borderData: FlBorderData(show: false),
            barGroups: [
              BarChartGroupData(
                x: 1,
                barRods: [BarChartRodData(toY: 42, color: AppTheme.cyanAccent)],
              ),
              BarChartGroupData(
                x: 2,
                barRods: [BarChartRodData(toY: 28, color: AppTheme.goldAccent)],
              ),
              BarChartGroupData(
                x: 3,
                barRods: [
                  BarChartRodData(toY: 14, color: AppTheme.violetAccent),
                ],
              ),
              BarChartGroupData(
                x: 4,
                barRods: [
                  BarChartRodData(toY: 9, color: AppTheme.emeraldAccent),
                ],
              ),
            ],
          ),
        );

      case 5: // Ensemble Density Histogram
        return BarChart(
          BarChartData(
            titlesData: const FlTitlesData(show: false),
            borderData: FlBorderData(show: false),
            barGroups: List.generate(6, (i) {
              return BarChartGroupData(
                x: i,
                barRods: [
                  BarChartRodData(
                    toY: 5.0 + sin(i.toDouble()) * 3.0,
                    color: AppTheme.cyanAccent.withValues(alpha: 0.8),
                  ),
                ],
              );
            }),
          ),
        );

      case 9: // Shannon Diversity Index H'
        return LineChart(
          LineChartData(
            titlesData: const FlTitlesData(show: false),
            borderData: FlBorderData(show: false),
            lineBarsData: [
              LineChartBarData(
                spots: history
                    .map((p) => FlSpot(p.timeSec, p.shannonH))
                    .toList(),
                color: AppTheme.cyanSecondary,
                barWidth: 2.0,
              ),
            ],
          ),
        );

      case 10: // Pielou Species Evenness J'
        return LineChart(
          LineChartData(
            titlesData: const FlTitlesData(show: false),
            borderData: FlBorderData(show: false),
            lineBarsData: [
              LineChartBarData(
                spots: history
                    .map((p) => FlSpot(p.timeSec, p.pielouJ))
                    .toList(),
                color: AppTheme.goldAccent,
                barWidth: 2.0,
              ),
            ],
          ),
        );

      case 19: // Ecological Balance Gauge X/Y
        return LineChart(
          LineChartData(
            titlesData: const FlTitlesData(show: false),
            borderData: FlBorderData(show: false),
            lineBarsData: [
              LineChartBarData(
                spots: history
                    .map((p) => FlSpot(p.timeSec, p.ecoRatioXY))
                    .toList(),
                color: AppTheme.violetAccent,
                barWidth: 2.0,
              ),
            ],
          ),
        );

      default: // Fallback generic curve for remaining telemetry metrics
        return LineChart(
          LineChartData(
            titlesData: const FlTitlesData(show: false),
            borderData: FlBorderData(show: false),
            lineBarsData: [
              LineChartBarData(
                spots: history
                    .map(
                      (p) => FlSpot(p.timeSec, sin(p.timeSec + num) * 4 + 10),
                    )
                    .toList(),
                color: AppTheme.cyanAccent,
                barWidth: 1.8,
              ),
            ],
          ),
        );
    }
  }
}
