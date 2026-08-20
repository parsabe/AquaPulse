import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_container.dart';
import '../providers/app_providers.dart';

class DrPaulyVoicePortalScreen extends ConsumerStatefulWidget {
  const DrPaulyVoicePortalScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<DrPaulyVoicePortalScreen> createState() => _DrPaulyVoicePortalScreenState();
}

class _DrPaulyVoicePortalScreenState extends ConsumerState<DrPaulyVoicePortalScreen> {
  final TextEditingController _queryController = TextEditingController();

  final List<String> sampleQuestionsEN = [
    "What is the extinction risk for Salmo trutta in boreal streams?",
    "Explain the acoustic sound output pressure level of Gadus morhua.",
    "How does Euler-Maruyama stochastic dynamics model Lotka-Volterra balance?",
  ];

  final List<String> sampleQuestionsDE = [
    "Wie hoch ist das Aussterberisiko für Salmo trutta in Fließgewässern?",
    "Erkläre den bioakustischen Schalldruckpegel von Gadus morhua.",
    "Wie modelliert die stochastische EnKF-Gleichung das ökologische Gleichgewicht?",
  ];

  @override
  Widget build(BuildContext context) {
    final voiceState = ref.watch(voiceAssistantProvider);
    final isGerman = voiceState.languageMode == 'DE';
    final sampleQuestions = isGerman ? sampleQuestionsDE : sampleQuestionsEN;

    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      body: SafeArea(
        child: Column(
          children: [
            // Screen Header & Language Toggle
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: GlassContainer(
                padding: const EdgeInsets.all(14),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: const BoxDecoration(
                        color: AppTheme.violetAccent,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.record_voice_over, color: Colors.white, size: 22),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "DR. PAUL PAULY VOICE ASSISTANT",
                            style: GoogleFonts.outfit(
                              color: AppTheme.textPrimary,
                              fontWeight: FontWeight.bold,
                              fontSize: 15,
                            ),
                          ),
                          Text(
                            "Ollama LLM Agent • ${voiceState.ollamaStatus}",
                            style: GoogleFonts.jetBrainsMono(
                              color: AppTheme.violetAccent,
                              fontSize: 10,
                            ),
                          ),
                        ],
                      ),
                    ),
                    // Language Switcher (EN / DE)
                    GestureDetector(
                      onTap: () {
                        ref.read(voiceAssistantProvider.notifier).toggleLanguage();
                      },
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: AppTheme.cyanAccent.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: AppTheme.cyanAccent),
                        ),
                        child: Text(
                          "LANG: ${voiceState.languageMode}",
                          style: GoogleFonts.jetBrainsMono(
                            color: AppTheme.cyanAccent,
                            fontWeight: FontWeight.bold,
                            fontSize: 11,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // Quick Sample Prompt Chips
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Row(
                children: sampleQuestions.map((q) {
                  return Padding(
                    padding: const EdgeInsets.only(right: 8.0),
                    child: ActionChip(
                      backgroundColor: AppTheme.bgCard,
                      side: BorderSide(color: AppTheme.cyanAccent.withOpacity(0.3)),
                      label: Text(
                        q,
                        style: GoogleFonts.outfit(color: AppTheme.textSecondary, fontSize: 11),
                      ),
                      onPressed: () {
                        _queryController.text = q;
                      },
                    ),
                  );
                }).toList(),
              ),
            ),

            const SizedBox(height: 10),

            // Conversation Chat Bubble List
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: voiceState.messages.length,
                itemBuilder: (context, index) {
                  final msg = voiceState.messages[index];
                  final isPauly = msg.sender == 'DR_PAULY';

                  return Padding(
                    padding: const EdgeInsets.only(bottom: 12.0),
                    child: Align(
                      alignment: isPauly ? Alignment.centerLeft : Alignment.centerRight,
                      child: GlassContainer(
                        width: MediaQuery.of(context).size.width * 0.82,
                        padding: const EdgeInsets.all(12),
                        backgroundColor: isPauly
                            ? AppTheme.bgCard.withOpacity(0.8)
                            : AppTheme.cyanAccent.withOpacity(0.15),
                        borderColor: isPauly ? AppTheme.violetAccent : AppTheme.cyanAccent,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Text(
                                  isPauly ? "DR. PAUL PAULY (LLM)" : "FIELD BIOLOGIST",
                                  style: GoogleFonts.jetBrainsMono(
                                    color: isPauly ? AppTheme.violetAccent : AppTheme.cyanAccent,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 10,
                                  ),
                                ),
                                const Spacer(),
                                Text(
                                  "${msg.timestamp.hour.toString().padLeft(2, '0')}:${msg.timestamp.minute.toString().padLeft(2, '0')}",
                                  style: GoogleFonts.jetBrainsMono(
                                    color: AppTheme.textMuted,
                                    fontSize: 9,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 6),
                            Text(
                              msg.text,
                              style: GoogleFonts.outfit(
                                color: AppTheme.textPrimary,
                                fontSize: 13,
                                height: 1.3,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),

            if (voiceState.isQuerying)
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const SizedBox(
                      width: 14,
                      height: 14,
                      child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.violetAccent),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      "Dr. Pauly querying Ollama LLM endpoint...",
                      style: GoogleFonts.jetBrainsMono(color: AppTheme.violetAccent, fontSize: 11),
                    ),
                  ],
                ),
              ),

            // Voice Mic & Query Input Terminal
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _queryController,
                      style: GoogleFonts.outfit(color: AppTheme.textPrimary),
                      decoration: InputDecoration(
                        hintText: isGerman
                            ? "Frage an Dr. Pauly stellen..."
                            : "Ask Dr. Pauly a field inquiry...",
                        hintStyle: GoogleFonts.outfit(color: AppTheme.textMuted, fontSize: 13),
                        filled: true,
                        fillColor: AppTheme.bgCard,
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(color: AppTheme.violetAccent.withOpacity(0.3)),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(color: AppTheme.violetAccent.withOpacity(0.3)),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: const BorderSide(color: AppTheme.violetAccent, width: 1.5),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  FloatingActionButton(
                    heroTag: "voice_send_btn",
                    backgroundColor: AppTheme.violetAccent,
                    onPressed: voiceState.isQuerying
                        ? null
                        : () {
                            final text = _queryController.text.trim();
                            if (text.isNotEmpty) {
                              ref.read(voiceAssistantProvider.notifier).sendQuery(text);
                              _queryController.clear();
                            }
                          },
                    child: const Icon(Icons.mic, color: Colors.white),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
