import 'dart:math';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_tts/flutter_tts.dart';

class JohnnyGlitchOverlay extends StatefulWidget {
  final Widget child;
  const JohnnyGlitchOverlay({super.key, required this.child});

  static _JohnnyGlitchOverlayState? of(BuildContext context) {
    return context.findAncestorStateOfType<_JohnnyGlitchOverlayState>();
  }

  @override
  State<JohnnyGlitchOverlay> createState() => _JohnnyGlitchOverlayState();
}

class _JohnnyGlitchOverlayState extends State<JohnnyGlitchOverlay>
    with SingleTickerProviderStateMixin {
  bool isJohnnyActive = false;
  String currentQuote = "";
  late AnimationController _glitchController;
  final FlutterTts _tts = FlutterTts();
  final Random _random = Random();

  final List<String> johnnyQuotes = [
    "Out here in the open water... it's pure biological freedom.",
    "Field telemetry is active. Focus on tracking the target specimens.",
    "Every specimen tracked today builds a clearer ecological map.",
    "Data assimilation streams look clear. Keep observing.",
    "Wake up, biologist... we've got an ocean ecosystem to save.",
  ];

  @override
  void initState() {
    super.initState();
    _glitchController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 150),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _glitchController.dispose();
    super.dispose();
  }

  void triggerJohnnyRelicGlitch([String? customQuote]) {
    final quote = customQuote ??
        johnnyQuotes[_random.nextInt(johnnyQuotes.length)];

    setState(() {
      isJohnnyActive = true;
      currentQuote = quote;
    });

    // TTS speech synthesis
    try {
      _tts.setSpeechRate(0.48);
      _tts.setPitch(0.85); // Cyberpunk voice pitch
      _tts.speak(quote);
    } catch (_) {}

    // Auto dismiss Johnny glitch overlay after 6.5 seconds
    Future.delayed(const Duration(milliseconds: 6500), () {
      if (mounted) {
        setState(() {
          isJohnnyActive = false;
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        widget.child,

        // FULL SCREEN JOHNNY SILVERHAND RELIC SYSTEM GLITCH OVERLAY
        if (isJohnnyActive)
          Positioned.fill(
            child: AnimatedBuilder(
              animation: _glitchController,
              builder: (context, child) {
                final glitchOffset = (_random.nextDouble() - 0.5) * 12.0;
                final isGlitchFrame = _random.nextDouble() > 0.4;

                return Scaffold(
                  backgroundColor: Colors.transparent,
                  body: Container(
                    decoration: BoxDecoration(
                      color: const Color(0xFF0F172A).withValues(alpha: 0.92),
                    ),
                    child: Stack(
                      children: [
                        // Cyber RGB Split Glitch Background Distortion Lines
                        if (isGlitchFrame)
                          Positioned(
                            top: _random.nextDouble() * MediaQuery.of(context).size.height,
                            left: 0,
                            right: 0,
                            height: _random.nextDouble() * 30 + 4,
                            child: Container(
                              color: (_random.nextBool()
                                      ? const Color(0xFFDE52AF)
                                      : const Color(0xFF00F0FF))
                                  .withValues(alpha: 0.4),
                            ),
                          ),

                        // Scanline Grid Overlay
                        CustomPaint(
                          size: Size.infinite,
                          painter: CyberScanlinePainter(_glitchController.value),
                        ),

                        // Center Johnny Relic Content
                        SafeArea(
                          child: Center(
                            child: Padding(
                              padding: const EdgeInsets.symmetric(horizontal: 24.0),
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  // Johnny Avatar Frame with Neon Glitch Border
                                  Transform.translate(
                                    offset: Offset(glitchOffset, 0),
                                    child: Container(
                                      width: 140,
                                      height: 140,
                                      decoration: BoxDecoration(
                                        shape: BoxShape.circle,
                                        color: const Color(0xFF1E293B),
                                        border: Border.all(
                                          color: const Color(0xFFDE52AF),
                                          width: 3.5,
                                        ),
                                        boxShadow: const [
                                          BoxShadow(
                                            color: Color(0xFFDE52AF),
                                            blurRadius: 25,
                                            spreadRadius: 4,
                                          ),
                                          BoxShadow(
                                            color: Color(0xFF00F0FF),
                                            blurRadius: 35,
                                            spreadRadius: 1,
                                          ),
                                        ],
                                      ),
                                      child: const ClipOval(
                                        child: Center(
                                          child: Icon(
                                            Icons.developer_board,
                                            color: Color(0xFFDE52AF),
                                            size: 72,
                                          ),
                                        ),
                                      ),
                                    ),
                                  ),

                                  const SizedBox(height: 20),

                                  // Relic Status Badge
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 14,
                                      vertical: 6,
                                    ),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFFDE52AF).withValues(alpha: 0.2),
                                      borderRadius: BorderRadius.circular(8),
                                      border: Border.all(
                                        color: const Color(0xFFDE52AF),
                                      ),
                                    ),
                                    child: Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        const Icon(
                                          Icons.warning_amber_rounded,
                                          color: Color(0xFFDE52AF),
                                          size: 16,
                                        ),
                                        const SizedBox(width: 8),
                                        Text(
                                          "JOHNNY SILVERHAND RELIC OVERRIDE [J]",
                                          style: GoogleFonts.jetBrainsMono(
                                            color: const Color(0xFFDE52AF),
                                            fontWeight: FontWeight.bold,
                                            fontSize: 11,
                                            letterSpacing: 1.1,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),

                                  const SizedBox(height: 24),

                                  // Full-Screen Spoken Dialogue Line Card
                                  Transform.translate(
                                    offset: Offset(-glitchOffset * 0.5, 0),
                                    child: Container(
                                      width: double.infinity,
                                      padding: const EdgeInsets.all(20),
                                      decoration: BoxDecoration(
                                        color: Colors.black.withValues(alpha: 0.85),
                                        borderRadius: BorderRadius.circular(16),
                                        border: Border.all(
                                          color: isGlitchFrame
                                              ? const Color(0xFF00F0FF)
                                              : const Color(0xFFDE52AF),
                                          width: 2.0,
                                        ),
                                        boxShadow: [
                                          BoxShadow(
                                            color: Colors.black.withValues(alpha: 0.6),
                                            blurRadius: 20,
                                            offset: const Offset(0, 8),
                                          ),
                                        ],
                                      ),
                                      child: Column(
                                        children: [
                                          Text(
                                            "\"$currentQuote\"",
                                            style: GoogleFonts.outfit(
                                              color: Colors.white,
                                              fontSize: 18,
                                              fontWeight: FontWeight.w600,
                                              height: 1.4,
                                            ),
                                            textAlign: TextAlign.center,
                                          ),
                                          const SizedBox(height: 12),
                                          Text(
                                            "— JOHNNY SILVERHAND (NEURAL ENGRAM)",
                                            style: GoogleFonts.jetBrainsMono(
                                              color: const Color(0xFF00F0FF),
                                              fontSize: 10,
                                              fontWeight: FontWeight.bold,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ),

                                  const SizedBox(height: 28),

                                  // Close Glitch Button
                                  OutlinedButton.icon(
                                    onPressed: () {
                                      setState(() {
                                        isJohnnyActive = false;
                                      });
                                    },
                                    icon: const Icon(
                                      Icons.power_settings_new,
                                      color: Color(0xFFDE52AF),
                                      size: 18,
                                    ),
                                    label: Text(
                                      "DISMISS RELIC OVERLAY",
                                      style: GoogleFonts.jetBrainsMono(
                                        color: const Color(0xFFDE52AF),
                                        fontWeight: FontWeight.bold,
                                        fontSize: 12,
                                      ),
                                    ),
                                    style: OutlinedButton.styleFrom(
                                      side: const BorderSide(
                                        color: Color(0xFFDE52AF),
                                      ),
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 20,
                                        vertical: 12,
                                      ),
                                      shape: RoundedRectangleBorder(
                                        borderRadius: BorderRadius.circular(10),
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
      ],
    );
  }
}

class CyberScanlinePainter extends CustomPainter {
  final double animValue;
  CyberScanlinePainter(this.animValue);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF00F0FF).withValues(alpha: 0.05)
      ..strokeWidth = 1.0;

    for (double y = 0; y < size.height; y += 4) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
