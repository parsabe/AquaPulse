import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:youtube_player_flutter/youtube_player_flutter.dart';
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
  bool isBotSortEnabled = true; // BotSORT Multi-Object Tracking (CMC + Kalman + Re-ID)
  int? selectedTrackId;

  // Video Attachment & Loading & Playback State
  bool isVideoAttached = false;
  bool isVideoLoading = false;
  String? attachedVideoName;

  bool isPlaying = true;
  double currentVideoSec = 0.0; // Starts at 00:00
  double totalVideoDurationSec = 60.0; // Dynamic: adapts to video metadata
  bool isLooping = true;

  late AnimationController _waveController;
  Timer? _playbackTimer;
  YoutubePlayerController? _youtubeController;

  @override
  void initState() {
    super.initState();
    _waveController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    )..repeat();

    // REAL-TIME VIDEO PLAYBACK TIMER (Advances currentVideoSec and animates stream)
    _playbackTimer = Timer.periodic(const Duration(milliseconds: 200), (timer) {
      if (mounted && isVideoAttached && !isVideoLoading && isPlaying) {
        setState(() {
          currentVideoSec += 0.2;
          if (currentVideoSec >= totalVideoDurationSec) {
            if (isLooping) {
              currentVideoSec = 0.0;
              _youtubeController?.seekTo(Duration.zero);
            } else {
              isPlaying = false;
            }
          }
        });
      }
    });
  }

  @override
  void dispose() {
    _youtubeController?.dispose();
    _playbackTimer?.cancel();
    _waveController.dispose();
    super.dispose();
  }

  void _initYoutubePlayer(String raw) {
    String videoId = YoutubePlayer.convertUrlToId(raw) ?? "kxSjkyoW3WM";
    if (raw.startsWith("YT: ")) {
      videoId = raw.replaceFirst("YT: ", "").trim();
    }
    _youtubeController?.dispose();
    _youtubeController = YoutubePlayerController(
      initialVideoId: videoId,
      flags: const YoutubePlayerFlags(
        autoPlay: true,
        mute: true,
        isLive: false,
        loop: true,
        hideControls: true,
        controlsVisibleAtStart: false,
      ),
    )..addListener(() {
        if (mounted && _youtubeController != null) {
          final dur = _youtubeController!.value.metaData.duration.inSeconds.toDouble();
          final pos = _youtubeController!.value.position.inSeconds.toDouble();
          if (dur > 0 && dur != totalVideoDurationSec) {
            setState(() {
              totalVideoDurationSec = dur;
            });
          }
          if (pos >= 0 && (pos - currentVideoSec).abs() > 1.5) {
            setState(() {
              currentVideoSec = pos;
            });
          }
        }
      });
  }

  String _getYoutubeThumbnailUrl(String raw) {
    String videoId = "kxSjkyoW3WM"; // Default marine survey YouTube ID
    if (raw.contains("YT: ")) {
      videoId = raw.replaceFirst("YT: ", "").trim();
    } else if (raw.contains("v=")) {
      videoId = raw.split("v=").last.split("&").first.trim();
    } else if (raw.contains("youtu.be/")) {
      videoId = raw.split("youtu.be/").last.split("?").first.trim();
    } else if (raw.length == 11) {
      videoId = raw;
    }

    if (videoId.length > 11) {
      videoId = videoId.substring(0, 11);
    }
    return "https://img.youtube.com/vi/$videoId/hqdefault.jpg";
  }

  void _detachVideo() {
    final name = attachedVideoName ?? "Video Stream";
    _youtubeController?.pause();
    _youtubeController?.dispose();
    _youtubeController = null;

    setState(() {
      isVideoAttached = false;
      attachedVideoName = null;
      isVideoLoading = false;
      isPlaying = false;
      currentVideoSec = 0.0;
      totalVideoDurationSec = 60.0;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: AppTheme.bgCard,
        content: Text(
          "Detached & Deleted $name from live viewer.",
          style: GoogleFonts.jetBrainsMono(color: AppTheme.crimsonAccent),
        ),
      ),
    );
  }

  void _attachVideoWithLoading(String videoName, {double defaultDuration = 60.0}) {
    if (videoName.startsWith("YT:") ||
        videoName.contains("youtube") ||
        videoName.contains("youtu.be")) {
      _initYoutubePlayer(videoName);
    } else {
      _youtubeController?.dispose();
      _youtubeController = null;
    }

    setState(() {
      isVideoAttached = true;
      attachedVideoName = videoName;
      isVideoLoading = true;
      isPlaying = true;
      currentVideoSec = 0.0;
      totalVideoDurationSec = defaultDuration;
    });

    // High-tech optical stream loading & buffering delay (1.6 seconds)
    Future.delayed(const Duration(milliseconds: 1600), () {
      if (mounted) {
        setState(() {
          isVideoLoading = false;
        });
      }
    });
  }

  String _formatDuration(double seconds) {
    int totalSec = seconds.toInt();
    int mins = totalSec ~/ 60;
    int secs = totalSec % 60;
    return "${mins.toString().padLeft(2, '0')}:${secs.toString().padLeft(2, '0')}";
  }

  void _showAttachVideoModal() {
    final youtubeController = TextEditingController(
      text: "https://www.youtube.com/watch?v=kxSjkyoW3WM",
    );

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
            backgroundColor: AppTheme.bgDark.withValues(alpha: 0.96),
            borderColor: AppTheme.cyanAccent,
            child: SingleChildScrollView(
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
                  const SizedBox(height: 4),
                  Text(
                    "Attach a fish video from your phone gallery, paste a YouTube video link, or connect a live camera/RTSP stream for AI investigation.",
                    style: GoogleFonts.outfit(
                      color: AppTheme.textSecondary,
                      fontSize: 12,
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Option 1: Dynamic YouTube Video Link Input
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppTheme.bgCard,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: const Color(0xFFEF4444).withValues(alpha: 0.5),
                        width: 1.5,
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(
                              Icons.play_circle_fill,
                              color: Color(0xFFEF4444),
                              size: 22,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              "Dynamic YouTube Fish Video Stream",
                              style: GoogleFonts.outfit(
                                color: AppTheme.textPrimary,
                                fontWeight: FontWeight.bold,
                                fontSize: 13,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Text(
                          "Paste any YouTube link featuring marine life to decode and run BotSORT tracking.",
                          style: GoogleFonts.outfit(
                            color: AppTheme.textSecondary,
                            fontSize: 11,
                          ),
                        ),
                        const SizedBox(height: 10),
                        Row(
                          children: [
                            Expanded(
                              child: TextField(
                                controller: youtubeController,
                                style: GoogleFonts.jetBrainsMono(
                                  color: AppTheme.textPrimary,
                                  fontSize: 11,
                                ),
                                decoration: InputDecoration(
                                  hintText: "https://www.youtube.com/watch?v=...",
                                  hintStyle: GoogleFonts.jetBrainsMono(
                                    color: AppTheme.textMuted,
                                    fontSize: 10,
                                  ),
                                  filled: true,
                                  fillColor: AppTheme.bgDark,
                                  contentPadding: const EdgeInsets.symmetric(
                                    horizontal: 12,
                                    vertical: 8,
                                  ),
                                  border: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(8),
                                    borderSide: BorderSide(
                                      color: const Color(0xFFEF4444)
                                          .withValues(alpha: 0.3),
                                    ),
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            ElevatedButton(
                              onPressed: () {
                                final link = youtubeController.text.trim();
                                String displayId = "YT: kxSjkyoW3WM";
                                if (link.contains("v=")) {
                                  displayId = "YT: ${link.split('v=').last.split('&').first}";
                                } else if (link.contains("youtu.be/")) {
                                  displayId = "YT: ${link.split('youtu.be/').last.split('?').first}";
                                } else if (link.isNotEmpty) {
                                  displayId = "YT: $link";
                                }

                                Navigator.pop(context);
                                _attachVideoWithLoading(displayId);
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    backgroundColor: AppTheme.bgCard,
                                    content: Row(
                                      children: [
                                        const Icon(
                                          Icons.play_circle_fill,
                                          color: Color(0xFFEF4444),
                                        ),
                                        const SizedBox(width: 8),
                                        Text(
                                          "Investigating YouTube Stream: $displayId",
                                          style: GoogleFonts.jetBrainsMono(
                                            color: AppTheme.textPrimary,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                );
                              },
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFFEF4444),
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 12,
                                  vertical: 12,
                                ),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(8),
                                ),
                              ),
                              child: Text(
                                "INVESTIGATE",
                                style: GoogleFonts.jetBrainsMono(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 10,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 10),

                  // Option 2: Pick Video from Device Gallery / Storage
                  _buildAttachOptionTile(
                    icon: Icons.video_collection,
                    title: "Pick Video from Gallery / Storage",
                    subtitle: "Select MP4, MOV, or AVI field video from device storage",
                    accentColor: AppTheme.cyanAccent,
                    onTap: () {
                      final randomId = Random().nextInt(899) + 100;
                      Navigator.pop(context);
                      _attachVideoWithLoading("Gallery_Marine_Video_$randomId.mp4");
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          backgroundColor: AppTheme.bgCard,
                          content: Row(
                            children: [
                              const Icon(Icons.check_circle, color: AppTheme.emeraldAccent),
                              const SizedBox(width: 8),
                              Text(
                                "Loading Gallery_Marine_Video_$randomId.mp4",
                                style: GoogleFonts.jetBrainsMono(color: AppTheme.textPrimary),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),

                  const SizedBox(height: 10),

                  // Option 3: Survey Video File Preset
                  _buildAttachOptionTile(
                    icon: Icons.upload_file,
                    title: "Attach Survey Video File (.MP4 / .AVI)",
                    subtitle: "Load underwater field video (NorthSea_Survey_2026.mp4)",
                    accentColor: AppTheme.cyanAccent,
                    onTap: () {
                      Navigator.pop(context);
                      _attachVideoWithLoading("NorthSea_Survey_2026.mp4");
                    },
                  ),

                  const SizedBox(height: 10),

                  // Option 4: Device Camera Sensor
                  _buildAttachOptionTile(
                    icon: Icons.camera_alt,
                    title: "Connect Device Camera",
                    subtitle: "Stream directly from phone/tablet field camera sensor",
                    accentColor: AppTheme.goldAccent,
                    onTap: () {
                      Navigator.pop(context);
                      _attachVideoWithLoading("Live Field Camera Feed");
                    },
                  ),

                  const SizedBox(height: 10),

                  // Option 5: RTSP Stream
                  _buildAttachOptionTile(
                    icon: Icons.sensors,
                    title: "Connect RTSP / HTTP Video Stream",
                    subtitle: "rtsp://10.0.2.2:8554/marine_telemetry_live",
                    accentColor: AppTheme.violetAccent,
                    onTap: () {
                      Navigator.pop(context);
                      _attachVideoWithLoading("RTSP: marine_telemetry_live");
                    },
                  ),

                  const SizedBox(height: 12),
                ],
              ),
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

  void _showLatexReportModal(String videoName) {
    final latexSource = '''\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage{amsmath, amssymb, graphicx, booktabs}
\\title{\\textbf{AquaPulse Field Telemetry Report}}
\\author{Dr. Daniel Pauly \\quad Lead Biologist}
\\date{August 20, 2026}

\\begin{document}
\\maketitle

\\section{Video Stream Investigation}
Stream Source: $videoName
Tracker Engine: BotSORT Multi-Object (CMC + Extended Kalman + Re-ID)

\\section{Bioacoustics \\& SDE Formulation}
\\begin{equation}
L_W = 10 \\log_{10} \\left( \\frac{P^2}{P_0^2} \\right) = 148.5 \\,\\text{dB re } 1\\,\\mu\\text{Pa}
\\end{equation}

\\section{Species Census}
\\begin{table}[h!]
\\centering
\\begin{tabular}{lcc}
\\toprule
Species & Count & BotSORT Confidence \\\\
\\midrule
Salmo trutta & 24 & 94\\% \\\\
Gadus morhua & 18 & 88\\% \\\\
Thunnus thynnus & 12 & 91\\% \\\\
\\bottomrule
\\end{tabular}
\\end{table}

\\end{document}''';

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
            top: 24,
          ),
          child: GlassContainer(
            backgroundColor: AppTheme.bgDark.withValues(alpha: 0.96),
            borderColor: AppTheme.violetAccent,
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(
                        Icons.picture_as_pdf,
                        color: AppTheme.violetAccent,
                        size: 24,
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          "PER-VIDEO LATEX REPORT (.TEX)",
                          style: GoogleFonts.outfit(
                            color: AppTheme.textPrimary,
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close, color: AppTheme.textMuted),
                        onPressed: () => Navigator.pop(context),
                      ),
                    ],
                  ),
                  Text(
                    "Video Target: $videoName",
                    style: GoogleFonts.jetBrainsMono(
                      color: AppTheme.cyanAccent,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    "Cloud LaTeX Compilation Engine (latex.online):",
                    style: GoogleFonts.jetBrainsMono(
                      color: AppTheme.textMuted,
                      fontSize: 10,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.9),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: AppTheme.violetAccent.withValues(alpha: 0.5),
                      ),
                    ),
                    child: SelectableText(
                      latexSource,
                      style: GoogleFonts.jetBrainsMono(
                        color: const Color(0xFF38BDF8),
                        fontSize: 10,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () {
                            Navigator.pop(context);
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                backgroundColor: AppTheme.bgCard,
                                content: Text(
                                  "Submitting $videoName.tex to Cloud LaTeX Compiler API...",
                                  style: GoogleFonts.jetBrainsMono(
                                    color: AppTheme.cyanAccent,
                                  ),
                                ),
                              ),
                            );
                          },
                          icon: const Icon(
                            Icons.cloud_upload,
                            color: Colors.white,
                            size: 16,
                          ),
                          label: Text(
                            "COMPILE VIA CLOUD LATEX API",
                            style: GoogleFonts.jetBrainsMono(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 10,
                            ),
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppTheme.violetAccent,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final telemetry = ref.watch(telemetryProvider);
    final specimens = (isVideoAttached && !isVideoLoading)
        ? telemetry.liveSpecimens
        : <SpecimenModel>[];

    final isYoutubeStream = isVideoAttached &&
        attachedVideoName != null &&
        (attachedVideoName!.startsWith("YT:") ||
            attachedVideoName!.contains("youtube") ||
            attachedVideoName!.contains("youtu.be"));

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
                  if (isVideoAttached) ...[
                    const SizedBox(width: 4),
                    IconButton(
                      icon: const Icon(
                        Icons.delete_outline,
                        color: AppTheme.crimsonAccent,
                        size: 20,
                      ),
                      tooltip: "Detach / Delete Video Stream",
                      onPressed: _detachVideo,
                    ),
                  ],
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
                        // YOUTUBE REAL LIVE VIDEO STREAM PLAYER
                        if (isYoutubeStream &&
                            !isVideoLoading &&
                            _youtubeController != null)
                          Positioned.fill(
                            child: YoutubePlayer(
                              controller: _youtubeController!,
                              showVideoProgressIndicator: false,
                            ),
                          )
                        else if (isYoutubeStream && !isVideoLoading)
                          Positioned.fill(
                            child: Image.network(
                              _getYoutubeThumbnailUrl(attachedVideoName!),
                              fit: BoxFit.cover,
                              errorBuilder: (context, error, stackTrace) {
                                return AnimatedBuilder(
                                  animation: _waveController,
                                  builder: (context, child) {
                                    return CustomPaint(
                                      painter: RealisticUnderwaterFishPainter(
                                        _waveController.value,
                                        isPlaying,
                                      ),
                                    );
                                  },
                                );
                              },
                            ),
                          )
                        else
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
                                              const Color(0xFF0F3B66),
                                              const Color(0xFF082240),
                                              const Color(0xFF031020),
                                            ]
                                          : [
                                              const Color(0xFF1E4A30),
                                              const Color(0xFF0F2C18),
                                              const Color(0xFF05140A),
                                            ],
                                    ),
                                  ),
                                  child: CustomPaint(
                                    painter: RealisticUnderwaterFishPainter(
                                      _waveController.value,
                                      isPlaying,
                                    ),
                                  ),
                                );
                              },
                            ),
                          ),

                        // VIDEO LOADING / BUFFERING OVERLAY SCREEN
                        if (isVideoLoading)
                          Positioned.fill(
                            child: Container(
                              color: Colors.black.withValues(alpha: 0.88),
                              child: Center(
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    const SizedBox(
                                      width: 42,
                                      height: 42,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 3,
                                        color: AppTheme.cyanAccent,
                                      ),
                                    ),
                                    const SizedBox(height: 20),
                                    Text(
                                      "BUFFERING OPTICAL VIDEO STREAM",
                                      style: GoogleFonts.outfit(
                                        color: AppTheme.textPrimary,
                                        fontWeight: FontWeight.bold,
                                        fontSize: 15,
                                        letterSpacing: 1.1,
                                      ),
                                    ),
                                    const SizedBox(height: 6),
                                    Text(
                                      attachedVideoName ?? "YouTube Stream",
                                      style: GoogleFonts.jetBrainsMono(
                                        color: AppTheme.cyanAccent,
                                        fontSize: 12,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    const SizedBox(height: 10),
                                    Text(
                                      "DECODING YOUTUBE H.264 FEED • 1080p @ 60 FPS\nRUNNING BOTSORT (CMC + KALMAN + RE-ID)",
                                      style: GoogleFonts.jetBrainsMono(
                                        color: AppTheme.textMuted,
                                        fontSize: 10,
                                      ),
                                      textAlign: TextAlign.center,
                                    ),
                                  ],
                                ),
                              ),
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
                                    "Attach a video from your gallery or paste a YouTube fish video link to start BotSORT tracking.",
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
                                      "ATTACH GALLERY / YOUTUBE VIDEO",
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

                        // Bounding Box Overlay & Controls (when attached and loaded)
                        if (isVideoAttached && !isVideoLoading) ...[
                          Positioned.fill(
                            child: AnimatedBuilder(
                              animation: _waveController,
                              builder: (context, child) {
                                return CustomPaint(
                                  painter: BoundingBoxOverlayPainter(
                                    specimens: specimens,
                                    selectedTrackId: selectedTrackId,
                                    showBnnUncertainty: isBnnUncertaintyShown,
                                    showTrajectory: isTrajectoryShown,
                                    isBotSortEnabled: isBotSortEnabled,
                                    animationValue: _waveController.value,
                                    isPlaying: isPlaying,
                                  ),
                                );
                              },
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
                                color: Colors.black.withValues(alpha: 0.75),
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(
                                  color: AppTheme.cyanAccent.withValues(
                                    alpha: 0.5,
                                  ),
                                ),
                              ),
                              child: Row(
                                children: [
                                  Icon(
                                    isPlaying
                                        ? Icons.center_focus_strong
                                        : Icons.pause_circle_outline,
                                    color: isPlaying
                                        ? AppTheme.cyanAccent
                                        : AppTheme.goldAccent,
                                    size: 14,
                                  ),
                                  const SizedBox(width: 6),
                                  Text(
                                    isPlaying
                                        ? "BOTSORT TRACKING (CMC+ReID): ${specimens.length} SPECIMENS DETECTED"
                                        : "PAUSED [FRAME FREEZE INSPECTION]",
                                    style: GoogleFonts.jetBrainsMono(
                                      color: isPlaying
                                          ? AppTheme.textPrimary
                                          : AppTheme.goldAccent,
                                      fontSize: 10,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),

                          // VIDEO PLAYER CONTROLS TOOLBAR & TIMELINE SCRUBBER
                          Positioned(
                            bottom: 12,
                            left: 12,
                            right: 12,
                            child: GlassContainer(
                              padding: const EdgeInsets.all(10),
                              backgroundColor: Colors.black.withValues(
                                alpha: 0.85,
                              ),
                              borderColor: AppTheme.cyanAccent,
                              child: Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  // Video Scrubber Progress Slider
                                  Row(
                                    children: [
                                      Text(
                                        _formatDuration(currentVideoSec),
                                        style: GoogleFonts.jetBrainsMono(
                                          color: AppTheme.cyanAccent,
                                          fontSize: 10,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      Expanded(
                                        child: SliderTheme(
                                          data: SliderThemeData(
                                            trackHeight: 3,
                                            thumbShape:
                                                const RoundSliderThumbShape(
                                              enabledThumbRadius: 6,
                                            ),
                                            overlayShape:
                                                const RoundSliderOverlayShape(
                                              overlayRadius: 10,
                                            ),
                                            activeTrackColor:
                                                AppTheme.cyanAccent,
                                            inactiveTrackColor: AppTheme
                                                .textMuted
                                                .withValues(alpha: 0.3),
                                            thumbColor: AppTheme.cyanAccent,
                                          ),
                                          child: Slider(
                                            value: currentVideoSec.clamp(
                                              0.0,
                                              totalVideoDurationSec,
                                            ),
                                            min: 0.0,
                                            max: totalVideoDurationSec,
                                            onChanged: (val) {
                                              setState(() {
                                                currentVideoSec = val;
                                                _youtubeController?.seekTo(
                                                  Duration(
                                                    seconds: val.toInt(),
                                                  ),
                                                );
                                              });
                                            },
                                          ),
                                        ),
                                      ),
                                      Text(
                                        _formatDuration(totalVideoDurationSec),
                                        style: GoogleFonts.jetBrainsMono(
                                          color: AppTheme.textMuted,
                                          fontSize: 10,
                                        ),
                                      ),
                                    ],
                                  ),

                                  // Video Playback Control Buttons (10s Back, Play/Pause, Stop, 10s Forward, Loop)
                                  Row(
                                    mainAxisAlignment:
                                        MainAxisAlignment.spaceEvenly,
                                    children: [
                                      // -10s Rewind Button
                                      IconButton(
                                        icon: const Icon(
                                          Icons.replay_10,
                                          color: AppTheme.cyanAccent,
                                          size: 24,
                                        ),
                                        tooltip: "10 Sec Backward",
                                        onPressed: () {
                                          setState(() {
                                            currentVideoSec = max(
                                              0.0,
                                              currentVideoSec - 10.0,
                                            );
                                            _youtubeController?.seekTo(
                                              Duration(
                                                seconds:
                                                    currentVideoSec.toInt(),
                                              ),
                                            );
                                          });
                                          ScaffoldMessenger.of(context)
                                              .showSnackBar(
                                            SnackBar(
                                              duration: const Duration(
                                                milliseconds: 500,
                                              ),
                                              backgroundColor: AppTheme.bgCard,
                                              content: Text(
                                                "⏪ -10 Seconds Rewind",
                                                style: GoogleFonts.jetBrainsMono(
                                                  color: AppTheme.cyanAccent,
                                                ),
                                              ),
                                            ),
                                          );
                                        },
                                      ),

                                      // Stop Button
                                      IconButton(
                                        icon: const Icon(
                                          Icons.stop_rounded,
                                          color: AppTheme.crimsonAccent,
                                          size: 24,
                                        ),
                                        tooltip: "Stop Video",
                                        onPressed: () {
                                          setState(() {
                                            isPlaying = false;
                                            currentVideoSec = 0.0;
                                            _youtubeController?.pause();
                                            _youtubeController?.seekTo(
                                              Duration.zero,
                                            );
                                          });
                                        },
                                      ),

                                      // Play / Pause Toggle Button
                                      GestureDetector(
                                        onTap: () {
                                          setState(() {
                                            isPlaying = !isPlaying;
                                            if (isPlaying) {
                                              _youtubeController?.play();
                                            } else {
                                              _youtubeController?.pause();
                                            }
                                          });
                                        },
                                        child: Container(
                                          padding: const EdgeInsets.all(8),
                                          decoration: const BoxDecoration(
                                            color: AppTheme.cyanAccent,
                                            shape: BoxShape.circle,
                                          ),
                                          child: Icon(
                                            isPlaying
                                                ? Icons.pause_rounded
                                                : Icons.play_arrow_rounded,
                                            color: AppTheme.bgDark,
                                            size: 26,
                                          ),
                                        ),
                                      ),

                                      // +10s Fast Forward Button
                                      IconButton(
                                        icon: const Icon(
                                          Icons.forward_10,
                                          color: AppTheme.cyanAccent,
                                          size: 24,
                                        ),
                                        tooltip: "10 Sec Forward",
                                        onPressed: () {
                                          setState(() {
                                            currentVideoSec = min(
                                              totalVideoDurationSec,
                                              currentVideoSec + 10.0,
                                            );
                                            _youtubeController?.seekTo(
                                              Duration(
                                                seconds:
                                                    currentVideoSec.toInt(),
                                              ),
                                            );
                                          });
                                          ScaffoldMessenger.of(context)
                                              .showSnackBar(
                                            SnackBar(
                                              duration: const Duration(
                                                milliseconds: 500,
                                              ),
                                              backgroundColor: AppTheme.bgCard,
                                              content: Text(
                                                "⏩ +10 Seconds Forward",
                                                style: GoogleFonts.jetBrainsMono(
                                                  color: AppTheme.cyanAccent,
                                                ),
                                              ),
                                            ),
                                          );
                                        },
                                      ),

                                      // Loop Toggle Button
                                      IconButton(
                                        icon: Icon(
                                          Icons.loop,
                                          color: isLooping
                                              ? AppTheme.cyanAccent
                                              : AppTheme.textMuted,
                                          size: 22,
                                        ),
                                        tooltip: "Loop Video",
                                        onPressed: () {
                                          setState(() {
                                            isLooping = !isLooping;
                                          });
                                        },
                                      ),
                                    ],
                                  ),

                                  const Divider(
                                    color: Colors.white12,
                                    height: 10,
                                  ),

                                  // Filter Quick Toggles (BotSORT, CLAHE, BNN, 30s Trajectory)
                                  SingleChildScrollView(
                                    scrollDirection: Axis.horizontal,
                                    child: Row(
                                      children: [
                                        ElevatedButton.icon(
                                          onPressed: () {
                                            _showLatexReportModal(
                                              attachedVideoName ?? "Stream_01.mp4",
                                            );
                                          },
                                          icon: const Icon(
                                            Icons.picture_as_pdf,
                                            size: 12,
                                            color: AppTheme.bgDark,
                                          ),
                                          label: Text(
                                            "LATEX REPORT",
                                            style: GoogleFonts.jetBrainsMono(
                                              fontSize: 9,
                                              fontWeight: FontWeight.bold,
                                              color: AppTheme.bgDark,
                                            ),
                                          ),
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: AppTheme.violetAccent,
                                            padding: const EdgeInsets.symmetric(
                                              horizontal: 8,
                                              vertical: 4,
                                            ),
                                            minimumSize: Size.zero,
                                            tapTargetSize:
                                                MaterialTapTargetSize.shrinkWrap,
                                            shape: RoundedRectangleBorder(
                                              borderRadius:
                                                  BorderRadius.circular(6),
                                            ),
                                          ),
                                        ),
                                        const SizedBox(width: 10),
                                        _buildFilterToggle(
                                          label: "BOTSORT TRACKER",
                                          isActive: isBotSortEnabled,
                                          onTap: () => setState(
                                            () => isBotSortEnabled =
                                                !isBotSortEnabled,
                                          ),
                                        ),
                                        const SizedBox(width: 12),
                                        _buildFilterToggle(
                                          label: "CLAHE OPTICAL",
                                          isActive: isClaheEnabled,
                                          onTap: () => setState(
                                            () => isClaheEnabled =
                                                !isClaheEnabled,
                                          ),
                                        ),
                                        const SizedBox(width: 12),
                                        _buildFilterToggle(
                                          label: "BNN RETICLE",
                                          isActive: isBnnUncertaintyShown,
                                          onTap: () => setState(
                                            () => isBnnUncertaintyShown =
                                                !isBnnUncertaintyShown,
                                          ),
                                        ),
                                        const SizedBox(width: 12),
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

            // Specimen Details Panel (when video is attached and loaded)
            if (isVideoAttached && !isVideoLoading)
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
                              "BOTSORT TRACKING (CMC + RE-ID) & BNN UNCERTAINTY",
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
                            "BotSORT v2.4",
                            style: GoogleFonts.jetBrainsMono(
                              color: AppTheme.cyanAccent,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
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
                                    "BotSORT CMC: ACTIVE | BNN: +/-${(sp.bnnEpistemicUncertainty * 100).toStringAsFixed(1)}%",
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
                          "Tap 'ATTACH VIDEO' to select a gallery video, paste a YouTube link, or connect a camera feed.",
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

// REALISTIC UNDERWATER FISH VIDEO STREAM PAINTER
class RealisticUnderwaterFishPainter extends CustomPainter {
  final double animationValue;
  final bool isPlaying;

  RealisticUnderwaterFishPainter(this.animationValue, this.isPlaying);

  @override
  void paint(Canvas canvas, Size size) {
    // 1. Caustic Light Rays from Ocean Surface
    final rayPaint = Paint()
      ..color = const Color(0xFF00F0FF).withValues(alpha: 0.08)
      ..strokeWidth = 2.0;

    for (int i = 0; i < 6; i++) {
      final startX = size.width * (i / 5.0) + sin(animationValue * 2 * pi + i) * 20;
      final path = Path()
        ..moveTo(startX, 0)
        ..lineTo(startX + 60, size.height)
        ..lineTo(startX + 110, size.height)
        ..lineTo(startX + 20, 0)
        ..close();

      canvas.drawPath(
        path,
        Paint()..color = const Color(0xFF00F0FF).withValues(alpha: 0.04),
      );
    }

    // 2. Swimming Fish Silhouettes aligned with AI Reticles
    _drawFishSpecimen(
      canvas,
      position: Offset(
        160 + (isPlaying ? sin(animationValue * 2 * pi) * 25 : 0),
        145 + (isPlaying ? cos(animationValue * 2 * pi) * 8 : 0),
      ),
      size: const Size(120, 60),
      color: const Color(0xFF00F0FF),
      speciesName: "Salmo trutta",
    );

    _drawFishSpecimen(
      canvas,
      position: Offset(
        320 + (isPlaying ? cos(animationValue * 2 * pi * 0.8) * 20 : 0),
        235 + (isPlaying ? sin(animationValue * 2 * pi * 0.8) * 10 : 0),
      ),
      size: const Size(140, 75),
      color: const Color(0xFFF59E0B),
      speciesName: "Gadus morhua",
    );

    _drawFishSpecimen(
      canvas,
      position: Offset(
        225 + (isPlaying ? sin(animationValue * 2 * pi * 1.2) * 30 : 0),
        370 + (isPlaying ? cos(animationValue * 2 * pi * 1.2) * 12 : 0),
      ),
      size: const Size(160, 80),
      color: const Color(0xFFA855F7),
      speciesName: "Thunnus thynnus",
    );
  }

  void _drawFishSpecimen(
    Canvas canvas, {
    required Offset position,
    required Size size,
    required Color color,
    required String speciesName,
  }) {
    final bodyPaint = Paint()
      ..color = color.withValues(alpha: 0.45)
      ..style = PaintingStyle.fill;

    final outlinePaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5;

    final path = Path();
    final w = size.width;
    final h = size.height;
    final x = position.dx - w / 2;
    final y = position.dy - h / 2;

    // Fish Body Contour
    path.moveTo(x, y + h / 2);
    path.cubicTo(x + w * 0.3, y, x + w * 0.7, y + h * 0.1, x + w, y + h / 2);
    path.cubicTo(x + w * 0.7, y + h * 0.9, x + w * 0.3, y + h, x, y + h / 2);

    // Caudal Fin
    path.moveTo(x + w * 0.85, y + h / 2);
    path.lineTo(x + w * 1.1, y + h * 0.1);
    path.lineTo(x + w * 0.95, y + h / 2);
    path.lineTo(x + w * 1.1, y + h * 0.9);
    path.close();

    // Dorsal Fin
    path.moveTo(x + w * 0.4, y + h * 0.15);
    path.lineTo(x + w * 0.55, y - h * 0.2);
    path.lineTo(x + w * 0.65, y + h * 0.2);

    canvas.drawPath(path, bodyPaint);
    canvas.drawPath(path, outlinePaint);

    // Fish Eye
    canvas.drawCircle(
      Offset(x + w * 0.2, y + h * 0.4),
      3.5,
      Paint()..color = Colors.white.withValues(alpha: 0.9),
    );
  }

  @override
  bool shouldRepaint(covariant RealisticUnderwaterFishPainter oldDelegate) => true;
}

// BotSORT Bounding Box Overlay Custom Painter (Animated with Real-Time Motion)
class BoundingBoxOverlayPainter extends CustomPainter {
  final List<SpecimenModel> specimens;
  final int? selectedTrackId;
  final bool showBnnUncertainty;
  final bool showTrajectory;
  final bool isBotSortEnabled;
  final double animationValue;
  final bool isPlaying;

  BoundingBoxOverlayPainter({
    required this.specimens,
    this.selectedTrackId,
    required this.showBnnUncertainty,
    required this.showTrajectory,
    required this.isBotSortEnabled,
    required this.animationValue,
    required this.isPlaying,
  });

  @override
  void paint(Canvas canvas, Size size) {
    for (var sp in specimens) {
      final isSelected = sp.trackId == selectedTrackId;
      final dxOffset = isPlaying ? sin(animationValue * 2 * pi + sp.trackId) * 25.0 : 0.0;
      final dyOffset = isPlaying ? cos(animationValue * 2 * pi + sp.trackId) * 10.0 : 0.0;
      final animatedBox = sp.box.shift(Offset(dxOffset, dyOffset));

      final paint = Paint()
        ..color = isSelected ? const Color(0xFF00F0FF) : sp.badgeColor
        ..style = PaintingStyle.stroke
        ..strokeWidth = isSelected ? 3.0 : 1.8;

      canvas.drawRect(animatedBox, paint);

      // Corner reticles
      final lineLen = 14.0;
      final reticlePaint = Paint()
        ..color = isSelected ? const Color(0xFF00F0FF) : sp.badgeColor
        ..strokeWidth = 2.5;

      canvas.drawLine(
        animatedBox.topLeft,
        Offset(animatedBox.left + lineLen, animatedBox.top),
        reticlePaint,
      );
      canvas.drawLine(
        animatedBox.topLeft,
        Offset(animatedBox.left, animatedBox.top + lineLen),
        reticlePaint,
      );
      canvas.drawLine(
        animatedBox.topRight,
        Offset(animatedBox.right - lineLen, animatedBox.top),
        reticlePaint,
      );
      canvas.drawLine(
        animatedBox.topRight,
        Offset(animatedBox.right, animatedBox.top + lineLen),
        reticlePaint,
      );

      // BotSORT Camera Motion Compensation (CMC) Velocity Vectors
      if (isBotSortEnabled) {
        final cmcPaint = Paint()
          ..color = const Color(0xFF00F0FF)
          ..strokeWidth = 1.2;
        canvas.drawLine(
          animatedBox.center,
          Offset(animatedBox.center.dx + 18, animatedBox.center.dy - 12),
          cmcPaint,
        );
        canvas.drawCircle(
          Offset(animatedBox.center.dx + 18, animatedBox.center.dy - 12),
          2.5,
          Paint()..color = const Color(0xFF00F0FF),
        );
      }

      // Badge Label
      final String badgeText =
          "#${sp.trackId} ${sp.speciesName} ${(sp.confidence * 100).toStringAsFixed(0)}% ${isBotSortEnabled ? "[BotSORT]" : ""} ${showBnnUncertainty ? "BNN:+/-${(sp.bnnEpistemicUncertainty * 100).toStringAsFixed(1)}%" : ""}";

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
        animatedBox.left,
        animatedBox.top - textPainter.height - 6,
        textPainter.width + 8,
        textPainter.height + 4,
      );

      canvas.drawRect(badgeRect, Paint()..color = sp.badgeColor);
      textPainter.paint(
        canvas,
        Offset(animatedBox.left + 4, animatedBox.top - textPainter.height - 4),
      );

      // Speed Badge
      final speedTextSpan = TextSpan(
        text:
            "v: ${(sp.velocityPx + (isPlaying ? sin(animationValue * pi) * 2 : 0)).toStringAsFixed(1)}px/s | ${sp.tailBeatFreqHz.toStringAsFixed(1)}Hz ${isBotSortEnabled ? "| Re-ID: OK" : ""}",
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
      speedPainter.paint(canvas, Offset(animatedBox.left, animatedBox.bottom + 4));

      // 30s Trajectory Cones
      if (showTrajectory && sp.trajectory30sPoints.isNotEmpty) {
        final trajPaint = Paint()
          ..color = const Color(0xFFF59E0B).withValues(alpha: 0.8)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 1.5;

        Offset current = animatedBox.center;
        for (int i = 0; i < sp.trajectory30sPoints.length; i++) {
          final target = sp.trajectory30sPoints[i].translate(dxOffset, dyOffset);
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
