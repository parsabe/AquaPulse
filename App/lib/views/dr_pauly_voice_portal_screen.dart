import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_container.dart';
import '../providers/app_providers.dart';
import '../services/ollama_voice_service.dart';

class DrPaulyVoicePortalScreen extends ConsumerStatefulWidget {
  const DrPaulyVoicePortalScreen({super.key});

  @override
  ConsumerState<DrPaulyVoicePortalScreen> createState() =>
      _DrPaulyVoicePortalScreenState();
}

class _DrPaulyVoicePortalScreenState
    extends ConsumerState<DrPaulyVoicePortalScreen> {
  final TextEditingController _queryController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final OllamaVoiceService _audioService = OllamaVoiceService();

  // Attached Fish Image State
  String? _selectedFishImage;

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
  void dispose() {
    _queryController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 350),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _showSelectFishImageModal() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return GlassContainer(
          margin: const EdgeInsets.all(16),
          backgroundColor: AppTheme.bgDark.withValues(alpha: 0.95),
          borderColor: AppTheme.cyanAccent,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(
                    Icons.add_a_photo,
                    color: AppTheme.cyanAccent,
                    size: 22,
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      "ATTACH FISH SPECIMEN PHOTO",
                      style: GoogleFonts.outfit(
                        color: AppTheme.textPrimary,
                        fontWeight: FontWeight.bold,
                        fontSize: 15,
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
                "Select a fish specimen photo for Dr. Daniel Pauly's morphological AI inspection.",
                style: GoogleFonts.outfit(
                  color: AppTheme.textSecondary,
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 14),

              _buildFishImageOption(
                fileName: "Salmo_trutta_specimen_042.jpg",
                speciesTag: "Brown Trout • Spawning Morph",
                icon: Icons.phishing,
                accentColor: AppTheme.cyanAccent,
              ),
              const SizedBox(height: 8),

              _buildFishImageOption(
                fileName: "Gadus_morhua_specimen_108.jpg",
                speciesTag: "Atlantic Cod • Benthopelagic",
                icon: Icons.set_meal,
                accentColor: AppTheme.goldAccent,
              ),
              const SizedBox(height: 8),

              _buildFishImageOption(
                fileName: "Thunnus_thynnus_specimen_219.jpg",
                speciesTag: "Bluefin Tuna • Pelagic Predator",
                icon: Icons.water,
                accentColor: AppTheme.violetAccent,
              ),
              const SizedBox(height: 8),

              _buildFishImageOption(
                fileName: "Field_Camera_Fish_Photo.jpg",
                speciesTag: "Upload from Device Camera / Gallery",
                icon: Icons.camera_alt,
                accentColor: AppTheme.emeraldAccent,
              ),
              const SizedBox(height: 10),
            ],
          ),
        );
      },
    );
  }

  Widget _buildFishImageOption({
    required String fileName,
    required String speciesTag,
    required IconData icon,
    required Color accentColor,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () {
          setState(() {
            _selectedFishImage = fileName;
          });
          Navigator.pop(context);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              backgroundColor: AppTheme.bgCard,
              content: Row(
                children: [
                  Icon(Icons.photo, color: accentColor),
                  const SizedBox(width: 8),
                  Text(
                    "Attached: $fileName",
                    style: GoogleFonts.jetBrainsMono(color: AppTheme.textPrimary),
                  ),
                ],
              ),
            ),
          );
        },
        borderRadius: BorderRadius.circular(10),
        child: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: AppTheme.bgCard,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: accentColor.withValues(alpha: 0.3),
            ),
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: accentColor.withValues(alpha: 0.15),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, color: accentColor, size: 18),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      fileName,
                      style: GoogleFonts.jetBrainsMono(
                        color: AppTheme.textPrimary,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                    Text(
                      speciesTag,
                      style: GoogleFonts.outfit(
                        color: AppTheme.textSecondary,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(Icons.add_circle_outline, color: accentColor, size: 18),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final voiceState = ref.watch(voiceAssistantProvider);
    final isGerman = voiceState.languageMode == 'DE';
    final sampleQuestions = isGerman ? sampleQuestionsDE : sampleQuestionsEN;

    // Auto-scroll chat to latest message at the bottom whenever messages update
    ref.listen<VoiceAssistantState>(voiceAssistantProvider, (previous, next) {
      if (previous?.messages.length != next.messages.length ||
          next.isQuerying != previous?.isQuerying) {
        _scrollToBottom();
      }
    });

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
                      child: const Icon(
                        Icons.record_voice_over,
                        color: Colors.white,
                        size: 22,
                      ),
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
                              fontSize: 14,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          Text(
                            "Ollama LLM Agent • ${voiceState.ollamaStatus}",
                            style: GoogleFonts.jetBrainsMono(
                              color: AppTheme.violetAccent,
                              fontSize: 10,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                    // Language Switcher (EN / DE)
                    GestureDetector(
                      onTap: () {
                        ref
                            .read(voiceAssistantProvider.notifier)
                            .toggleLanguage();
                      },
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: AppTheme.cyanAccent.withValues(alpha: 0.2),
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
                      side: BorderSide(
                        color: AppTheme.cyanAccent.withValues(alpha: 0.3),
                      ),
                      label: Text(
                        q,
                        style: GoogleFonts.outfit(
                          color: AppTheme.textSecondary,
                          fontSize: 11,
                        ),
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

            // Conversation Chat Bubble List (Bottom-anchored Auto-scrolling)
            Expanded(
              child: ListView.builder(
                controller: _scrollController,
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: voiceState.messages.length,
                itemBuilder: (context, index) {
                  final msg = voiceState.messages[index];
                  final isPauly = msg.sender == 'DR_PAULY';

                  return Padding(
                    padding: const EdgeInsets.only(bottom: 12.0),
                    child: Align(
                      alignment: isPauly
                          ? Alignment.centerLeft
                          : Alignment.centerRight,
                      child: GlassContainer(
                        width: MediaQuery.of(context).size.width * 0.90,
                        padding: const EdgeInsets.all(14),
                        backgroundColor: isPauly
                            ? AppTheme.bgCard.withValues(alpha: 0.88)
                            : AppTheme.cyanAccent.withValues(alpha: 0.15),
                        borderColor: isPauly
                            ? AppTheme.violetAccent
                            : AppTheme.cyanAccent,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(
                                  isPauly ? Icons.psychology : Icons.person,
                                  color: isPauly
                                      ? AppTheme.violetAccent
                                      : AppTheme.cyanAccent,
                                  size: 16,
                                ),
                                const SizedBox(width: 6),
                                Text(
                                  isPauly
                                      ? "DR. DANIEL PAULY (LLM)"
                                      : "FIELD BIOLOGIST",
                                  style: GoogleFonts.jetBrainsMono(
                                    color: isPauly
                                        ? AppTheme.violetAccent
                                        : AppTheme.cyanAccent,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 10,
                                  ),
                                ),
                                const Spacer(),
                                if (isPauly) ...[
                                  IconButton(
                                    icon: const Icon(
                                      Icons.volume_up,
                                      size: 18,
                                      color: AppTheme.violetAccent,
                                    ),
                                    padding: EdgeInsets.zero,
                                    constraints: const BoxConstraints(),
                                    onPressed: () {
                                      _audioService.speakText(
                                        msg.text,
                                        voiceState.languageMode,
                                      );
                                    },
                                  ),
                                  const SizedBox(width: 8),
                                ],
                                Text(
                                  "${msg.timestamp.hour.toString().padLeft(2, '0')}:${msg.timestamp.minute.toString().padLeft(2, '0')}",
                                  style: GoogleFonts.jetBrainsMono(
                                    color: AppTheme.textMuted,
                                    fontSize: 10,
                                  ),
                                ),
                              ],
                            ),

                            // Display Attached Fish Image Badge in Chat Bubble
                            if (msg.attachedFishImage != null) ...[
                              const SizedBox(height: 8),
                              Container(
                                padding: const EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: AppTheme.bgDark.withValues(alpha: 0.7),
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(
                                    color: AppTheme.cyanAccent.withValues(alpha: 0.5),
                                  ),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    const Icon(
                                      Icons.image,
                                      color: AppTheme.cyanAccent,
                                      size: 16,
                                    ),
                                    const SizedBox(width: 8),
                                    Text(
                                      "Attached Fish Photo: ${msg.attachedFishImage}",
                                      style: GoogleFonts.jetBrainsMono(
                                        color: AppTheme.cyanAccent,
                                        fontSize: 11,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],

                            const SizedBox(height: 8),
                            SelectableText(
                              msg.text,
                              style: GoogleFonts.outfit(
                                color: AppTheme.textPrimary,
                                fontSize: 13.5,
                                height: 1.4,
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
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: AppTheme.violetAccent,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      "Dr. Pauly inspecting fish specimen & querying LLM...",
                      style: GoogleFonts.jetBrainsMono(
                        color: AppTheme.violetAccent,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ),

            // Display Active Attached Fish Photo Banner above Input Field
            if (_selectedFishImage != null)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 4.0),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: AppTheme.cyanAccent.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: AppTheme.cyanAccent),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.phishing, color: AppTheme.cyanAccent, size: 16),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          "Fish Photo Attached: $_selectedFishImage",
                          style: GoogleFonts.jetBrainsMono(
                            color: AppTheme.cyanAccent,
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      GestureDetector(
                        onTap: () => setState(() => _selectedFishImage = null),
                        child: const Icon(Icons.close, color: AppTheme.cyanAccent, size: 16),
                      ),
                    ],
                  ),
                ),
              ),

            // Voice Mic & Query Input Terminal
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                children: [
                  // Attach Fish Photo Button
                  IconButton(
                    icon: const Icon(
                      Icons.add_a_photo,
                      color: AppTheme.cyanAccent,
                    ),
                    tooltip: "Attach Fish Photo",
                    onPressed: _showSelectFishImageModal,
                  ),
                  const SizedBox(width: 4),

                  Expanded(
                    child: TextField(
                      controller: _queryController,
                      style: GoogleFonts.outfit(color: AppTheme.textPrimary),
                      decoration: InputDecoration(
                        hintText: isGerman
                            ? "Frage / Fischfoto analysieren..."
                            : "Ask question or analyze attached fish photo...",
                        hintStyle: GoogleFonts.outfit(
                          color: AppTheme.textMuted,
                          fontSize: 13,
                        ),
                        filled: true,
                        fillColor: AppTheme.bgCard,
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 12,
                        ),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(
                            color: AppTheme.violetAccent.withValues(alpha: 0.3),
                          ),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(
                            color: AppTheme.violetAccent.withValues(alpha: 0.3),
                          ),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: const BorderSide(
                            color: AppTheme.violetAccent,
                            width: 1.5,
                          ),
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
                            if (text.isNotEmpty || _selectedFishImage != null) {
                              ref.read(voiceAssistantProvider.notifier).sendQuery(
                                    text,
                                    attachedFishImage: _selectedFishImage,
                                  );
                              _queryController.clear();
                              setState(() {
                                _selectedFishImage = null;
                              });
                              _scrollToBottom();
                            }
                          },
                    child: const Icon(Icons.send, color: Colors.white),
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
