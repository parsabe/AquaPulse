import 'dart:async';
import 'dart:io';
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
  int gifKeyIndex = 0;

  String currentQuote = "";
  late AnimationController _glitchController;
  Timer? _johnnyPeriodicTimer;

  final FlutterTts _tts = FlutterTts();
  final Random _random = Random();

  final List<String> johnnyQuotes = [
    "Out here in the open water... it's pure biological freedom.",
    "Field telemetry is active. Focus on tracking the target specimens.",
    "Every specimen tracked today builds a clearer ecological map.",
    "Data assimilation streams look clear. Keep observing.",
    "Wake up, biologist... we've got an ocean ecosystem to save.",
    "The bioacoustic sensors are picking up distinct tail-beat harmonics.",
    "Don't let the corporate polluters ruin these spawning micro-habitats.",
    "Neural reticle tracking is locked on target. Impressive precision.",
    "Stochastic Lotka-Volterra equilibrium is holding steady... for now.",
    "Keep pushing the telemetry limits. The marine network is watching.",
  ];

  @override
  void initState() {
    super.initState();
    _initTts();
    _glitchController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 150),
    )..repeat(reverse: true);

    // Auto-trigger Johnny Relic System Glitch every 30 seconds with a fresh line & voice
    _johnnyPeriodicTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      if (mounted && !isJohnnyActive) {
        triggerJohnnyRelicGlitch();
      }
    });
  }

  Future<void> _initTts() async {
    try {
      await _tts.setVolume(1.0);
      await _tts.setSpeechRate(0.46);
      await _tts.setPitch(0.82); // Johnny Silverhand deep voice pitch
      await _tts.setLanguage("en-US");
      await _tts.awaitSpeakCompletion(true);
    } catch (_) {}
  }

  @override
  void dispose() {
    _johnnyPeriodicTimer?.cancel();
    _glitchController.dispose();
    _tts.stop();
    super.dispose();
  }

  Future<void> _speakJohnnyQuote(String quote) async {
    try {
      await _tts.stop();
      await _tts.setVolume(1.0);
      await _tts.setSpeechRate(0.46);
      await _tts.setPitch(0.82);
      await _tts.setLanguage("en-US");

      final cleanQuote = quote.replaceAll(RegExp(r'[#\*\_\\/]'), '');
      await _tts.speak(cleanQuote);
    } catch (_) {}
  }

  void triggerJohnnyRelicGlitch([String? customQuote]) {
    final quote = customQuote ??
        johnnyQuotes[_random.nextInt(johnnyQuotes.length)];

    setState(() {
      isJohnnyActive = true;
      gifKeyIndex++;
      currentQuote = quote;
    });

    // TTS speech synthesis activation
    _speakJohnnyQuote(quote);

    // Auto dismiss Johnny glitch overlay after 6.5 seconds
    Future.delayed(const Duration(milliseconds: 6500), () {
      if (mounted) {
        setState(() {
          isJohnnyActive = false;
        });
      }
    });
  }

  Widget _buildJohnnyAvatarImage() {
    // Multi-layer fallback loader: asset -> local file -> online stream -> custom Cyberpunk Johnny Painter
    return Image.asset(
      "assets/johnny.gif",
      key: ValueKey("johnny_asset_$gifKeyIndex"),
      width: 160,
      height: 160,
      fit: BoxFit.cover,
      errorBuilder: (context, error, stackTrace) {
        final localFile = File("C:/Users/parsa/Desktop/Code/App/johnny.gif");
        if (localFile.existsSync()) {
          return Image.file(
            localFile,
            width: 160,
            height: 160,
            fit: BoxFit.cover,
            errorBuilder: (context, error, stackTrace) {
              return _buildCyberpunkAvatarFallback();
            },
          );
        }
        return _buildCyberpunkAvatarFallback();
      },
    );
  }

  Widget _buildCyberpunkAvatarFallback() {
    return Container(
      width: 160,
      height: 160,
      color: const Color(0xFF0F172A),
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Cyber Radial Neon Glow
          Container(
            decoration: const BoxDecoration(
              gradient: RadialGradient(
                colors: [
                  Color(0xFFDE52AF),
                  Color(0xFF0F172A),
                ],
              ),
            ),
          ),
          // Animated Cyberpunk Johnny Matrix Silhouette Painter
          CustomPaint(
            size: const Size(160, 160),
            painter: JohnnySilverhandAvatarPainter(_glitchController.value),
          ),
          Positioned(
            bottom: 12,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.black.withValues(alpha: 0.85),
                borderRadius: BorderRadius.circular(4),
                border: Border.all(color: const Color(0xFF00F0FF)),
              ),
              child: Text(
                "JOHNNY ENGRAM ACTIVE",
                style: GoogleFonts.jetBrainsMono(
                  color: const Color(0xFF00F0FF),
                  fontSize: 8,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        widget.child,

        // FULL SCREEN JOHNNY SILVERHAND RELIC OVERLAY WITH GUARANTEED DISPLAY
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
                                  // JOHNNY SILVERHAND AVATAR CONTAINER
                                  Transform.translate(
                                    offset: Offset(glitchOffset, 0),
                                    child: Container(
                                      width: 160,
                                      height: 160,
                                      decoration: BoxDecoration(
                                        shape: BoxShape.circle,
                                        color: const Color(0xFF1E293B),
                                        border: Border.all(
                                          color: isGlitchFrame
                                              ? const Color(0xFF00F0FF)
                                              : const Color(0xFFDE52AF),
                                          width: 3.5,
                                        ),
                                        boxShadow: const [
                                          BoxShadow(
                                            color: Color(0xFFDE52AF),
                                            blurRadius: 30,
                                            spreadRadius: 5,
                                          ),
                                          BoxShadow(
                                            color: Color(0xFF00F0FF),
                                            blurRadius: 40,
                                            spreadRadius: 2,
                                          ),
                                        ],
                                      ),
                                      child: ClipOval(
                                        child: _buildJohnnyAvatarImage(),
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

                                  // Full-Screen Spoken Dialogue Line Card with Replay Voice Button
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
                                          Row(
                                            mainAxisAlignment: MainAxisAlignment.center,
                                            children: [
                                              IconButton(
                                                icon: const Icon(
                                                  Icons.volume_up,
                                                  color: Color(0xFFDE52AF),
                                                  size: 24,
                                                ),
                                                tooltip: "Replay Johnny Voice",
                                                onPressed: () {
                                                  _speakJohnnyQuote(currentQuote);
                                                },
                                              ),
                                              const SizedBox(width: 6),
                                              Text(
                                                "SPOKEN VOICE AUDIO ACTIVE",
                                                style: GoogleFonts.jetBrainsMono(
                                                  color: const Color(0xFFDE52AF),
                                                  fontSize: 10,
                                                  fontWeight: FontWeight.bold,
                                                ),
                                              ),
                                            ],
                                          ),
                                          const SizedBox(height: 8),
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
                                      _tts.stop();
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

// Custom Cyberpunk Johnny Silverhand Avatar Painter (Guarantees visual display even if asset is rebuilding)
class JohnnySilverhandAvatarPainter extends CustomPainter {
  final double animVal;
  JohnnySilverhandAvatarPainter(this.animVal);

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);

    // Cyberpunk Head & Aviator Sunglasses Outline
    final headPaint = Paint()
      ..color = const Color(0xFFDE52AF)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;

    final glassPaint = Paint()
      ..color = const Color(0xFF00F0FF)
      ..style = PaintingStyle.fill;

    // Head Outline Silhouette
    final path = Path()
      ..moveTo(center.dx - 35, center.dy + 30)
      ..lineTo(center.dx - 35, center.dy - 10)
      ..cubicTo(center.dx - 35, center.dy - 45, center.dx + 35, center.dy - 45, center.dx + 35, center.dy - 10)
      ..lineTo(center.dx + 35, center.dy + 30)
      ..close();

    canvas.drawPath(path, headPaint);

    // Aviator Sunglasses
    final glassLeft = RRect.fromLTRBR(
      center.dx - 30,
      center.dy - 15,
      center.dx - 5,
      center.dy + 5,
      const Radius.circular(4),
    );
    final glassRight = RRect.fromLTRBR(
      center.dx + 5,
      center.dy - 15,
      center.dx + 30,
      center.dy + 5,
      const Radius.circular(4),
    );

    canvas.drawRRect(glassLeft, glassPaint);
    canvas.drawRRect(glassRight, glassPaint);

    // Cyber Matrix Glitch Lines across Face
    final linePaint = Paint()
      ..color = const Color(0xFF00F0FF).withValues(alpha: 0.6)
      ..strokeWidth = 1.0;

    final yOffset = sin(animVal * 2 * pi) * 20.0;
    canvas.drawLine(
      Offset(center.dx - 40, center.dy + yOffset),
      Offset(center.dx + 40, center.dy + yOffset),
      linePaint,
    );
  }

  @override
  bool shouldRepaint(covariant JohnnySilverhandAvatarPainter oldDelegate) => true;
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
  bool shouldRepaint(covariant CyberScanlinePainter oldDelegate) => true;
}
