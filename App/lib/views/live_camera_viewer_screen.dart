import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_container.dart';
import '../providers/app_providers.dart';
import '../models/specimen_model.dart';

class LiveCameraViewerScreen extends ConsumerStatefulWidget {
  const LiveCameraViewerScreen({super.key});

  @override
  ConsumerState<LiveCameraViewerScreen> createState() =>
      _LiveCameraViewerScreenState();
}

class _LiveCameraViewerScreenState extends ConsumerState<LiveCameraViewerScreen>
    with SingleTickerProviderStateMixin {
  bool isClaheEnabled = true;
  bool isBnnUncertaintyShown = true;
  bool isTrajectoryShown = true;
  int? selectedTrackId;
  late AnimationController _waveController;

  @override
  void initState() {
    super.initState();
    _waveController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    )..repeat();
  }

  @override
  void dispose() {
    _waveController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final telemetry = ref.watch(telemetryProvider);
    final specimens = telemetry.liveSpecimens;

    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      body: SafeArea(
        child: Column(
          children: [
            // Top Telemetry Header Bar
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 16.0,
                vertical: 8.0,
              ),
              child: Row(
                children: [
                  Container(
                    width: 10,
                    height: 10,
                    decoration: const BoxDecoration(
                      color: AppTheme.cyanAccent,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: AppTheme.cyanAccent,
                          blurRadius: 8,
                          spreadRadius: 2,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    "LIVE RTSP/CAM STREAM",
                    style: GoogleFonts.jetBrainsMono(
                      color: AppTheme.textPrimary,
                      fontWeight: FontWeight.bold,
                      fontSize: 13,
                    ),
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: AppTheme.bgCard,
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(
                        color: AppTheme.cyanAccent.withValues(alpha: 0.3),
                      ),
                    ),
                    child: Text(
                      "${telemetry.streamFps.toStringAsFixed(1)} FPS | 1080p60",
                      style: GoogleFonts.jetBrainsMono(
                        color: AppTheme.cyanAccent,
                        fontSize: 11,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Live Stream Viewport Container
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: GlassContainer(
                  padding: EdgeInsets.zero,
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: Stack(
                      children: [
                        // Synthetic Underwater Ocean Viewport Background
                        Positioned.fill(
                          child: AnimatedBuilder(
                            animation: _waveController,
                            builder: (context, child) {
                              return Container(
                                decoration: BoxDecoration(
                                  gradient: LinearGradient(
                                    begin: Alignment.topCenter,
                                    end: Alignment.bottomCenter,
                                    colors: isClaheEnabled
                                        ? [
                                            const Color(0xFF0F2B48),
                                            const Color(0xFF081B30),
                                            const Color(0xFF030D1A),
                                          ]
                                        : [
                                            const Color(0xFF1E3A20),
                                            const Color(0xFF0F2212),
                                            const Color(0xFF050E06),
                                          ],
                                  ),
                                ),
                                child: CustomPaint(
                                  painter: OceanWavePainter(
                                    _waveController.value,
                                  ),
                                ),
                              );
                            },
                          ),
                        ),

                        // Render Target Bounding Box Reticles & BNN Bounds
                        Positioned.fill(
                          child: CustomPaint(
                            painter: BoundingBoxOverlayPainter(
                              specimens: specimens,
                              selectedTrackId: selectedTrackId,
                              showBnnUncertainty: isBnnUncertaintyShown,
                              showTrajectory: isTrajectoryShown,
                            ),
                          ),
                        ),

                        // Interactive Touch Layer for Specimen Selection
                        Positioned.fill(
                          child: GestureDetector(
                            onTapDown: (details) {
                              final clickPos = details.localPosition;
                              for (var sp in specimens) {
                                if (sp.box.contains(clickPos)) {
                                  setState(() {
                                    selectedTrackId = sp.trackId;
                                  });
                                  break;
                                }
                              }
                            },
                          ),
                        ),

                        // Top Controls Overlay Badge
                        Positioned(
                          top: 12,
                          left: 12,
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 6,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.black.withValues(alpha: 0.65),
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(
                                color: AppTheme.cyanAccent.withValues(
                                  alpha: 0.4,
                                ),
                              ),
                            ),
                            child: Row(
                              children: [
                                const Icon(
                                  Icons.center_focus_strong,
                                  color: AppTheme.cyanAccent,
                                  size: 14,
                                ),
                                const SizedBox(width: 6),
                                Text(
                                  "TRACKING: ${specimens.length} SPECIMENS DETECTED",
                                  style: GoogleFonts.jetBrainsMono(
                                    color: AppTheme.textPrimary,
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),

                        // Bottom Viewport Controls Toolbar
                        Positioned(
                          bottom: 12,
                          left: 12,
                          right: 12,
                          child: GlassContainer(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 6,
                            ),
                            backgroundColor: Colors.black.withValues(
                              alpha: 0.7,
                            ),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceAround,
                              children: [
                                _buildFilterToggle(
                                  label: "CLAHE OPTICAL",
                                  isActive: isClaheEnabled,
                                  onTap: () => setState(
                                    () => isClaheEnabled = !isClaheEnabled,
                                  ),
                                ),
                                _buildFilterToggle(
                                  label: "BNN RETICLE",
                                  isActive: isBnnUncertaintyShown,
                                  onTap: () => setState(
                                    () => isBnnUncertaintyShown =
                                        !isBnnUncertaintyShown,
                                  ),
                                ),
                                _buildFilterToggle(
                                  label: "30S TRAJECTORY",
                                  isActive: isTrajectoryShown,
                                  onTap: () => setState(
                                    () =>
                                        isTrajectoryShown = !isTrajectoryShown,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),

            const SizedBox(height: 12),

            // Live Specimen Reticle Details Panel
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 16.0,
                vertical: 6.0,
              ),
              child: GlassContainer(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(
                          Icons.memory,
                          color: AppTheme.goldAccent,
                          size: 16,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            "NEURAL RETICLE & BNN UNCERTAINTY BOUNDS",
                            style: GoogleFonts.outfit(
                              color: AppTheme.textPrimary,
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          "EMD Kalman EMA",
                          style: GoogleFonts.jetBrainsMono(
                            color: AppTheme.textMuted,
                            fontSize: 10,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        children: specimens.map((sp) {
                          final isSelected = sp.trackId == selectedTrackId;
                          return Container(
                            margin: const EdgeInsets.only(right: 10),
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: isSelected
                                  ? AppTheme.cyanAccent.withValues(alpha: 0.15)
                                  : AppTheme.bgCard,
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(
                                color: isSelected
                                    ? AppTheme.cyanAccent
                                    : AppTheme.textMuted.withValues(alpha: 0.3),
                                width: isSelected ? 1.5 : 1,
                              ),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  "#${sp.trackId} ${sp.speciesName}",
                                  style: GoogleFonts.jetBrainsMono(
                                    color: sp.badgeColor,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 12,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  "Conf: ${(sp.confidence * 100).toStringAsFixed(0)}% | Speed: ${sp.velocityPx.toStringAsFixed(1)}px/s",
                                  style: GoogleFonts.outfit(
                                    color: AppTheme.textSecondary,
                                    fontSize: 11,
                                  ),
                                ),
                                Text(
                                  "BNN: +/-${(sp.bnnEpistemicUncertainty * 100).toStringAsFixed(1)}% [${(sp.bnnLowerConf * 100).toStringAsFixed(0)}-${(sp.bnnUpperConf * 100).toStringAsFixed(0)}%]",
                                  style: GoogleFonts.jetBrainsMono(
                                    color: AppTheme.goldAccent,
                                    fontSize: 10,
                                  ),
                                ),
                              ],
                            ),
                          );
                        }).toList(),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }

  Widget _buildFilterToggle({
    required String label,
    required bool isActive,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Row(
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: isActive ? AppTheme.cyanAccent : AppTheme.textMuted,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 6),
          Text(
            label,
            style: GoogleFonts.jetBrainsMono(
              color: isActive ? AppTheme.textPrimary : AppTheme.textMuted,
              fontSize: 10,
              fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
            ),
          ),
        ],
      ),
    );
  }
}

// Bounding Box Overlay Custom Painter
class BoundingBoxOverlayPainter extends CustomPainter {
  final List<SpecimenModel> specimens;
  final int? selectedTrackId;
  final bool showBnnUncertainty;
  final bool showTrajectory;

  BoundingBoxOverlayPainter({
    required this.specimens,
    this.selectedTrackId,
    required this.showBnnUncertainty,
    required this.showTrajectory,
  });

  @override
  void paint(Canvas canvas, Size size) {
    for (var sp in specimens) {
      final isSelected = sp.trackId == selectedTrackId;
      final paint = Paint()
        ..color = isSelected ? const Color(0xFF00F0FF) : sp.badgeColor
        ..style = PaintingStyle.stroke
        ..strokeWidth = isSelected ? 3.0 : 1.8;

      canvas.drawRect(sp.box, paint);

      // Corner reticles
      final lineLen = 14.0;
      final reticlePaint = Paint()
        ..color = isSelected ? const Color(0xFF00F0FF) : sp.badgeColor
        ..strokeWidth = 2.5;

      canvas.drawLine(
        sp.box.topLeft,
        Offset(sp.box.left + lineLen, sp.box.top),
        reticlePaint,
      );
      canvas.drawLine(
        sp.box.topLeft,
        Offset(sp.box.left, sp.box.top + lineLen),
        reticlePaint,
      );
      canvas.drawLine(
        sp.box.topRight,
        Offset(sp.box.right - lineLen, sp.box.top),
        reticlePaint,
      );
      canvas.drawLine(
        sp.box.topRight,
        Offset(sp.box.right, sp.box.top + lineLen),
        reticlePaint,
      );

      // Badge Label
      final String badgeText =
          "#${sp.trackId} ${sp.speciesName} ${(sp.confidence * 100).toStringAsFixed(0)}% ${showBnnUncertainty ? "BNN:+/-${(sp.bnnEpistemicUncertainty * 100).toStringAsFixed(1)}%" : ""}";

      final textSpan = TextSpan(
        text: badgeText,
        style: GoogleFonts.jetBrainsMono(
          color: Colors.black,
          fontSize: 10,
          fontWeight: FontWeight.bold,
        ),
      );
      final textPainter = TextPainter(
        text: textSpan,
        textDirection: TextDirection.ltr,
      );
      textPainter.layout();

      final badgeRect = Rect.fromLTWH(
        sp.box.left,
        sp.box.top - textPainter.height - 6,
        textPainter.width + 8,
        textPainter.height + 4,
      );

      canvas.drawRect(badgeRect, Paint()..color = sp.badgeColor);
      textPainter.paint(
        canvas,
        Offset(sp.box.left + 4, sp.box.top - textPainter.height - 4),
      );

      // Speed Badge
      final speedTextSpan = TextSpan(
        text:
            "v: ${sp.velocityPx.toStringAsFixed(1)}px/s | ${sp.tailBeatFreqHz.toStringAsFixed(1)}Hz",
        style: GoogleFonts.jetBrainsMono(
          color: const Color(0xFF00F0FF),
          fontSize: 9,
        ),
      );
      final speedPainter = TextPainter(
        text: speedTextSpan,
        textDirection: TextDirection.ltr,
      );
      speedPainter.layout();
      speedPainter.paint(canvas, Offset(sp.box.left, sp.box.bottom + 4));

      // 30s Trajectory Cones
      if (showTrajectory && sp.trajectory30sPoints.isNotEmpty) {
        final trajPaint = Paint()
          ..color = const Color(0xFFF59E0B).withValues(alpha: 0.8)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 1.5;

        Offset current = sp.box.center;
        for (int i = 0; i < sp.trajectory30sPoints.length; i++) {
          final target = sp.trajectory30sPoints[i];
          canvas.drawLine(current, target, trajPaint);
          canvas.drawCircle(
            target,
            (2 + i * 2.5),
            Paint()..color = const Color(0xFFF59E0B).withValues(alpha: 0.4),
          );
          current = target;
        }
      }
    }
  }

  @override
  bool shouldRepaint(covariant BoundingBoxOverlayPainter oldDelegate) => true;
}

class OceanWavePainter extends CustomPainter {
  final double animationValue;
  OceanWavePainter(this.animationValue);

  @override
  void paint(Canvas canvas, Size size) {
    final wavePaint = Paint()
      ..color = const Color(0xFF00F0FF).withValues(alpha: 0.04)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2;

    final path = Path();
    for (double x = 0; x < size.width; x += 20) {
      final y =
          size.height * 0.4 +
          sin((x / size.width * 4 * pi) + animationValue * 2 * pi) * 15;
      if (x == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }
    canvas.drawPath(path, wavePaint);
  }

  @override
  bool shouldRepaint(covariant OceanWavePainter oldDelegate) => true;
}
