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

class _LiveCameraViewerScreenState
    extends ConsumerState<LiveCameraViewerScreen>
    with SingleTickerProviderStateMixin {
  bool isClaheEnabled = true;
  bool isBnnUncertaintyShown = true;
  bool isTrajectoryShown = true;
  int? selectedTrackId;

  // Video Attachment State
  bool isVideoAttached = false;
  String? attachedVideoName;
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

  void _showAttachVideoModal() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) {
        return Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(context).viewInsets.bottom + 16,
            left: 16,
            right: 16,
            top: 16,
          ),
          child: GlassContainer(
            backgroundColor: AppTheme.bgDark.withValues(alpha: 0.95),
            borderColor: AppTheme.cyanAccent,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(
                      Icons.video_library,
                      color: AppTheme.cyanAccent,
                      size: 24,
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        "ATTACH MARINE VIDEO STREAM",
                        style: GoogleFonts.outfit(
                          color: AppTheme.textPrimary,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, color: AppTheme.textMuted),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  "Select a field video file, RTSP stream URL, or device camera feed to activate real-time specimen tracking.",
                  style: GoogleFonts.outfit(
                    color: AppTheme.textSecondary,
                    fontSize: 13,
                  ),
                ),
                const SizedBox(height: 18),

                // Option 1: Attach Survey Video File
                _buildAttachOptionTile(
                  icon: Icons.upload_file,
                  title: "Attach Survey Video File (.MP4 / .AVI)",
                  subtitle: "Load local underwater field video (NorthSea_Survey_2026.mp4)",
                  accentColor: AppTheme.cyanAccent,
                  onTap: () {
                    setState(() {
                      isVideoAttached = true;
                      attachedVideoName = "NorthSea_Survey_2026.mp4";
                    });
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        backgroundColor: AppTheme.bgCard,
                        content: Row(
                          children: [
                            const Icon(Icons.check_circle, color: AppTheme.emeraldAccent),
                            const SizedBox(width: 8),
                            Text(
                              "Attached NorthSea_Survey_2026.mp4 (1080p60)",
                              style: GoogleFonts.jetBrainsMono(color: AppTheme.textPrimary),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),

                const SizedBox(height: 10),

                // Option 2: Device Camera Feed
                _buildAttachOptionTile(
                  icon: Icons.camera_alt,
                  title: "Connect Device Camera",
                  subtitle: "Stream directly from phone/tablet field camera sensor",
                  accentColor: AppTheme.goldAccent,
                  onTap: () {
                    setState(() {
                      isVideoAttached = true;
                      attachedVideoName = "Live Field Camera Feed";
                    });
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        backgroundColor: AppTheme.bgCard,
                        content: Row(
                          children: [
                            const Icon(Icons.videocam, color: AppTheme.goldAccent),
                            const SizedBox(width: 8),
                            Text(
                              "Device Camera Stream Connected",
                              style: GoogleFonts.jetBrainsMono(color: AppTheme.textPrimary),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),

                const SizedBox(height: 10),

                // Option 3: RTSP URL Stream
                _buildAttachOptionTile(
                  icon: Icons.sensors,
                  title: "Connect RTSP / HTTP Video Stream",
                  subtitle: "rtsp://10.0.2.2:8554/marine_telemetry_live",
                  accentColor: AppTheme.violetAccent,
                  onTap: () {
                    setState(() {
                      isVideoAttached = true;
                      attachedVideoName = "RTSP: marine_telemetry_live";
                    });
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        backgroundColor: AppTheme.bgCard,
                        content: Row(
                          children: [
                            const Icon(Icons.sensors, color: AppTheme.violetAccent),
                            const SizedBox(width: 8),
                            Text(
                              "RTSP Stream Connected (8554/live)",
                              style: GoogleFonts.jetBrainsMono(color: AppTheme.textPrimary),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),

                const SizedBox(height: 12),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildAttachOptionTile({
    required IconData icon,
    required String title,
    required String subtitle,
    required Color accentColor,
    required VoidCallback onTap,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: AppTheme.bgCard,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: accentColor.withValues(alpha: 0.3),
              width: 1,
            ),
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: accentColor.withValues(alpha: 0.15),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, color: accentColor, size: 20),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: GoogleFonts.outfit(
                        color: AppTheme.textPrimary,
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      subtitle,
                      style: GoogleFonts.outfit(
                        color: AppTheme.textSecondary,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.chevron_right,
                color: accentColor,
                size: 20,
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final telemetry = ref.watch(telemetryProvider);
    final specimens = isVideoAttached ? telemetry.liveSpecimens : <SpecimenModel>[];

    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      body: SafeArea(
        child: Column(
          children: [
            // Top Header Bar
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
                    decoration: BoxDecoration(
                      color: isVideoAttached ? AppTheme.cyanAccent : AppTheme.goldAccent,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: isVideoAttached ? AppTheme.cyanAccent : AppTheme.goldAccent,
                          blurRadius: 8,
                          spreadRadius: 2,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      isVideoAttached
                          ? "STREAM: ${attachedVideoName ?? 'LIVE'}"
                          : "NO VIDEO ATTACHED",
                      style: GoogleFonts.jetBrainsMono(
                        color: AppTheme.textPrimary,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton.icon(
                    onPressed: _showAttachVideoModal,
                    icon: Icon(
                      isVideoAttached ? Icons.swap_horiz : Icons.add_a_photo,
                      size: 14,
                      color: AppTheme.bgDark,
                    ),
                    label: Text(
                      isVideoAttached ? "CHANGE VIDEO" : "ATTACH VIDEO",
                      style: GoogleFonts.jetBrainsMono(
                        fontWeight: FontWeight.bold,
                        fontSize: 11,
                        color: AppTheme.bgDark,
                      ),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.cyanAccent,
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      minimumSize: Size.zero,
                      tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
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

                        // Prompt Banner Overlay when video is not attached yet
                        if (!isVideoAttached)
                          Positioned.fill(
                            child: Container(
                              color: Colors.black.withValues(alpha: 0.65),
                              padding: const EdgeInsets.all(24),
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Container(
                                    padding: const EdgeInsets.all(20),
                                    decoration: BoxDecoration(
                                      color: AppTheme.cyanAccent.withValues(alpha: 0.15),
                                      shape: BoxShape.circle,
                                      border: Border.all(
                                        color: AppTheme.cyanAccent,
                                        width: 2,
                                      ),
                                    ),
                                    child: const Icon(
                                      Icons.video_call_rounded,
                                      color: AppTheme.cyanAccent,
                                      size: 48,
                                    ),
                                  ),
                                  const SizedBox(height: 20),
                                  Text(
                                    "ATTACH MARINE TELEMETRY VIDEO",
                                    style: GoogleFonts.outfit(
                                      color: AppTheme.textPrimary,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 18,
                                      letterSpacing: 1.1,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    "Please attach a marine survey video file, RTSP stream URL, or camera feed to start AI reticle tracking.",
                                    style: GoogleFonts.outfit(
                                      color: AppTheme.textSecondary,
                                      fontSize: 13,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                  const SizedBox(height: 24),
                                  ElevatedButton.icon(
                                    onPressed: _showAttachVideoModal,
                                    icon: const Icon(
                                      Icons.file_upload_outlined,
                                      color: AppTheme.bgDark,
                                    ),
                                    label: Text(
                                      "ATTACH VIDEO FILE / STREAM",
                                      style: GoogleFonts.jetBrainsMono(
                                        color: AppTheme.bgDark,
                                        fontWeight: FontWeight.bold,
                                        fontSize: 13,
                                      ),
                                    ),
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: AppTheme.cyanAccent,
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 24,
                                        vertical: 14,
                                      ),
                                      shape: RoundedRectangleBorder(
                                        borderRadius: BorderRadius.circular(12),
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),

                        // Bounding Box Overlay & Controls (when attached)
                        if (isVideoAttached) ...[
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
                                      () => isTrajectoryShown =
                                          !isTrajectoryShown,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              ),
            ),

            const SizedBox(height: 12),

            // Specimen Details Panel (when video is attached)
            if (isVideoAttached)
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

            if (!isVideoAttached)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 6.0),
                child: GlassContainer(
                  padding: const EdgeInsets.all(14),
                  child: Row(
                    children: [
                      const Icon(Icons.info_outline, color: AppTheme.cyanAccent, size: 18),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          "Tap 'ATTACH VIDEO' to select a field video recording or camera stream to enable live telemetry.",
                          style: GoogleFonts.outfit(
                            color: AppTheme.textSecondary,
                            fontSize: 12,
                          ),
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
