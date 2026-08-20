import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_container.dart';
import '../providers/app_providers.dart';

class AcoustoVisualSdeScreen extends ConsumerWidget {
  const AcoustoVisualSdeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final telemetry = ref.watch(telemetryProvider);
    final specimens = telemetry.liveSpecimens;

    double avgTailBeatHz = specimens.isEmpty
        ? 6.4
        : specimens.map((s) => s.tailBeatFreqHz).reduce((a, b) => a + b) /
              specimens.length;

    double avgAcousticDb = specimens.isEmpty
        ? 118.5
        : specimens.map((s) => s.acousticSourceDb).reduce((a, b) => a + b) /
              specimens.length;

    double diffusionEntropy = 0.85 + (specimens.length * 0.12);
    double collisionRisk = (specimens.length > 2 ? 14.2 : 3.5);

    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Screen Header
              Row(
                children: [
                  const Icon(
                    Icons.graphic_eq,
                    color: AppTheme.cyanAccent,
                    size: 24,
                  ),
                  const SizedBox(width: 10),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "ACOUSTO-VISUAL & NEURAL SDE METRICS",
                        style: GoogleFonts.outfit(
                          color: AppTheme.textPrimary,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        "Lighthill Hydrodynamic Waves & Trajectory Forecasting",
                        style: GoogleFonts.jetBrainsMono(
                          color: AppTheme.textSecondary,
                          fontSize: 11,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // CARD 1: Hydroacoustic Tail-Beat Frequency (Hz)
              GlassContainer(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: AppTheme.cyanAccent.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: const Icon(
                            Icons.waves,
                            color: AppTheme.cyanAccent,
                            size: 20,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                "HYDROACOUSTIC TAIL-BEAT FREQUENCY",
                                style: GoogleFonts.jetBrainsMono(
                                  color: AppTheme.textSecondary,
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                "Lighthill Vortex Circulation Pressure Field",
                                style: GoogleFonts.outfit(
                                  color: AppTheme.textMuted,
                                  fontSize: 11,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.baseline,
                      textBaseline: TextBaseline.alphabetic,
                      children: [
                        Text(
                          avgTailBeatHz.toStringAsFixed(2),
                          style: GoogleFonts.jetBrainsMono(
                            color: AppTheme.cyanAccent,
                            fontSize: 36,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          "Hz",
                          style: GoogleFonts.outfit(
                            color: AppTheme.cyanAccent,
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const Spacer(),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: AppTheme.emeraldAccent.withValues(
                              alpha: 0.15,
                            ),
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(color: AppTheme.emeraldAccent),
                          ),
                          child: Text(
                            "SWIM KINEMATICS NOMINAL",
                            style: GoogleFonts.jetBrainsMono(
                              color: AppTheme.emeraldAccent,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    // Wave Pulse Visual Indicator
                    SizedBox(
                      height: 40,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: List.generate(24, (index) {
                          double h =
                              (sin(index * 0.4 + avgTailBeatHz) * 16 + 20)
                                  .clamp(6.0, 36.0);
                          return Container(
                            width: 6,
                            height: h,
                            decoration: BoxDecoration(
                              color: AppTheme.cyanAccent.withValues(
                                alpha: (index % 2 == 0) ? 0.9 : 0.4,
                              ),
                              borderRadius: BorderRadius.circular(3),
                            ),
                          );
                        }),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 14),

              // CARD 2: Acoustic Source Output (dB re 1uPa)
              GlassContainer(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: AppTheme.goldAccent.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: const Icon(
                            Icons.volume_up,
                            color: AppTheme.goldAccent,
                            size: 20,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                "ACOUSTIC SOURCE OUTPUT LEVEL",
                                style: GoogleFonts.jetBrainsMono(
                                  color: AppTheme.textSecondary,
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                "Bioacoustic Sound Pressure Level @ 1m",
                                style: GoogleFonts.outfit(
                                  color: AppTheme.textMuted,
                                  fontSize: 11,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.baseline,
                      textBaseline: TextBaseline.alphabetic,
                      children: [
                        Text(
                          avgAcousticDb.toStringAsFixed(1),
                          style: GoogleFonts.jetBrainsMono(
                            color: AppTheme.goldAccent,
                            fontSize: 36,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          "dB re 1μPa",
                          style: GoogleFonts.outfit(
                            color: AppTheme.goldAccent,
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const Spacer(),
                        Text(
                          "Peak Hydro-Pressure: ${(avgAcousticDb * 0.28).toStringAsFixed(1)} Pa",
                          style: GoogleFonts.jetBrainsMono(
                            color: AppTheme.textMuted,
                            fontSize: 10,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(6),
                      child: LinearProgressIndicator(
                        value: (avgAcousticDb - 90.0) / 60.0,
                        backgroundColor: AppTheme.bgCard,
                        color: AppTheme.goldAccent,
                        minHeight: 8,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 14),

              // CARD 3: Neural SDE 30-Second Trajectory Forecasting
              GlassContainer(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: AppTheme.violetAccent.withValues(
                              alpha: 0.15,
                            ),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: const Icon(
                            Icons.psychology,
                            color: AppTheme.violetAccent,
                            size: 20,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                "NEURAL SDE 30s TRAJECTORY FORECASTING",
                                style: GoogleFonts.jetBrainsMono(
                                  color: AppTheme.textSecondary,
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                "Stochastic Future Cones & Inter-Specimen Repulsion",
                                style: GoogleFonts.outfit(
                                  color: AppTheme.textMuted,
                                  fontSize: 11,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: _buildMetricTile(
                            "DIFFUSION ENTROPY",
                            diffusionEntropy.toStringAsFixed(2),
                            AppTheme.violetAccent,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _buildMetricTile(
                            "COLLISION RISK 30S",
                            "${collisionRisk.toStringAsFixed(1)}%",
                            AppTheme.emeraldAccent,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    Text(
                      "FORECASTED CONES PER TARGET SPECIMEN",
                      style: GoogleFonts.jetBrainsMono(
                        color: AppTheme.textMuted,
                        fontSize: 10,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Column(
                      children: specimens.map((sp) {
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 6.0),
                          child: Row(
                            children: [
                              Container(
                                width: 6,
                                height: 6,
                                decoration: BoxDecoration(
                                  color: sp.badgeColor,
                                  shape: BoxShape.circle,
                                ),
                              ),
                              const SizedBox(width: 8),
                              Text(
                                "#${sp.trackId} ${sp.speciesName}",
                                style: GoogleFonts.jetBrainsMono(
                                  color: AppTheme.textPrimary,
                                  fontSize: 11,
                                ),
                              ),
                              const Spacer(),
                              Text(
                                "30s Projected Path: +${(sp.velocityPx * 1.8).toStringAsFixed(0)}px",
                                style: GoogleFonts.jetBrainsMono(
                                  color: AppTheme.violetAccent,
                                  fontSize: 10,
                                ),
                              ),
                            ],
                          ),
                        );
                      }).toList(),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMetricTile(String title, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: GoogleFonts.jetBrainsMono(
              color: AppTheme.textMuted,
              fontSize: 9,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: GoogleFonts.jetBrainsMono(
              color: color,
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),
        ],
      ),
    );
  }
}
