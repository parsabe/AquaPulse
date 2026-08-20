import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/specimen_model.dart';
import '../models/taxonomy_model.dart';
import '../models/telemetry_data_point.dart';
import '../services/database_service.dart';
import '../services/gbif_api_service.dart';
import '../services/telemetry_engine_service.dart';
import '../services/ollama_voice_service.dart';

// --- TELEMETRY ENGINE STATE & PROVIDER ---
class TelemetryState {
  final List<SpecimenModel> liveSpecimens;
  final TelemetryDataPoint currentPoint;
  final List<TelemetryDataPoint> history;
  final double extinctionRiskPercent;
  final double bifurcationIndexPercent;
  final bool isAlarmActive;
  final double streamFps;

  TelemetryState({
    required this.liveSpecimens,
    required this.currentPoint,
    required this.history,
    required this.extinctionRiskPercent,
    required this.bifurcationIndexPercent,
    required this.isAlarmActive,
    required this.streamFps,
  });

  TelemetryState copyWith({
    List<SpecimenModel>? liveSpecimens,
    TelemetryDataPoint? currentPoint,
    List<TelemetryDataPoint>? history,
    double? extinctionRiskPercent,
    double? bifurcationIndexPercent,
    bool? isAlarmActive,
    double? streamFps,
  }) {
    return TelemetryState(
      liveSpecimens: liveSpecimens ?? this.liveSpecimens,
      currentPoint: currentPoint ?? this.currentPoint,
      history: history ?? this.history,
      extinctionRiskPercent:
          extinctionRiskPercent ?? this.extinctionRiskPercent,
      bifurcationIndexPercent:
          bifurcationIndexPercent ?? this.bifurcationIndexPercent,
      isAlarmActive: isAlarmActive ?? this.isAlarmActive,
      streamFps: streamFps ?? this.streamFps,
    );
  }
}

class TelemetryNotifier extends StateNotifier<TelemetryState> {
  final TelemetryEngineService _engine = TelemetryEngineService();
  Timer? _timer;

  TelemetryNotifier()
      : super(TelemetryState(
          liveSpecimens: [],
          currentPoint: TelemetryDataPoint(
            timeSec: 0,
            preyX: 10.0,
            predY: 5.0,
            extinctionRiskPct: 8.4,
            bifurcationIndexPct: 12.5,
            shannonH: 1.5,
            pielouJ: 0.8,
            kalmanGainX: 0.35,
            kalmanGainY: 0.18,
            innovationResidual: 0.1,
            velocityMagnitude: 4.5,
            covarianceTrace: 0.5,
            ecoRatioXY: 2.0,
            detectionFps: 30.0,
          ),
          history: [],
          extinctionRiskPercent: 8.4,
          bifurcationIndexPercent: 12.5,
          isAlarmActive: false,
          streamFps: 60.0,
        )) {
    _startSimulation();
  }

  void _startSimulation() {
    _timer = Timer.periodic(const Duration(milliseconds: 150), (timer) {
      final point = _engine.step(yoloPreyObservation: 10.0);
      final currentSpecimens = _engine.generateLiveSpecimens();
      final risk = point.extinctionRiskPct;
      final bifurcation = point.bifurcationIndexPct;
      final alarm = (risk > 35.0 || bifurcation > 50.0);

      state = state.copyWith(
        liveSpecimens: currentSpecimens,
        currentPoint: point,
        history: List.from(_engine.history),
        extinctionRiskPercent: risk,
        bifurcationIndexPercent: bifurcation,
        isAlarmActive: alarm,
      );
    });
  }

  void triggerEnvironmentalShock(String shockType) {
    _engine.injectShock(shockType);
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }
}

final telemetryProvider =
    StateNotifierProvider<TelemetryNotifier, TelemetryState>((ref) {
  return TelemetryNotifier();
});

// --- OFFLINE TAXONOMY STATE & PROVIDER ---
class TaxonomyNotifier extends StateNotifier<List<TaxonomyModel>> {
  final GbifApiService _apiService = GbifApiService();

  TaxonomyNotifier() : super([]) {
    loadTaxonomy();
  }

  Future<void> loadTaxonomy() async {
    final list = await DatabaseService.instance.getAllTaxonomy();
    state = list;
  }

  Future<void> searchAndSyncSpecies(String speciesName) async {
    await _apiService.fetchAndCacheSpecies(speciesName);
    await loadTaxonomy();
  }

  Future<void> incrementCensus(String speciesName) async {
    await DatabaseService.instance.updateCensusCount(speciesName, 1);
    await loadTaxonomy();
  }
}

final taxonomyProvider =
    StateNotifierProvider<TaxonomyNotifier, List<TaxonomyModel>>((ref) {
  return TaxonomyNotifier();
});

// --- VOICE ASSISTANT STATE & PROVIDER ---
class VoiceChatMessage {
  final String sender; // 'USER' or 'DR_PAULY'
  final String text;
  final DateTime timestamp;
  final String language;
  final String? attachedFishImage; // E.g. 'Salmo_trutta_specimen_042.jpg'

  VoiceChatMessage({
    required this.sender,
    required this.text,
    required this.timestamp,
    required this.language,
    this.attachedFishImage,
  });
}

class VoiceAssistantState {
  final List<VoiceChatMessage> messages;
  final String languageMode; // 'EN' or 'DE'
  final bool isQuerying;
  final bool isSpeaking;
  final String ollamaStatus;

  VoiceAssistantState({
    required this.messages,
    this.languageMode = 'EN',
    this.isQuerying = false,
    this.isSpeaking = false,
    this.ollamaStatus = 'ONLINE (LOCAL 11434)',
  });

  VoiceAssistantState copyWith({
    List<VoiceChatMessage>? messages,
    String? languageMode,
    bool? isQuerying,
    bool? isSpeaking,
    String? ollamaStatus,
  }) {
    return VoiceAssistantState(
      messages: messages ?? this.messages,
      languageMode: languageMode ?? this.languageMode,
      isQuerying: isQuerying ?? this.isQuerying,
      isSpeaking: isSpeaking ?? this.isSpeaking,
      ollamaStatus: ollamaStatus ?? this.ollamaStatus,
    );
  }
}

class VoiceAssistantNotifier extends StateNotifier<VoiceAssistantState> {
  final OllamaVoiceService _voiceService = OllamaVoiceService();

  VoiceAssistantNotifier()
      : super(VoiceAssistantState(
          messages: [
            VoiceChatMessage(
              sender: 'DR_PAULY',
              text:
                  "Welcome to field telemetry portal. I am Dr. Daniel Pauly. Ask any ecological, bioacoustic, or species photo question in English or German.",
              timestamp: DateTime.now(),
              language: 'EN',
            )
          ],
        ));

  void toggleLanguage() {
    final nextLang = state.languageMode == 'EN' ? 'DE' : 'EN';
    state = state.copyWith(languageMode: nextLang);
  }

  Future<void> sendQuery(
    String userQuestion, {
    String? speciesContext,
    String? attachedFishImage,
  }) async {
    if (userQuestion.trim().isEmpty && attachedFishImage == null) return;

    final promptText = userQuestion.trim().isNotEmpty
        ? userQuestion
        : "Please inspect the attached fish photo ($attachedFishImage) for taxonomic identification and morphological traits.";

    final userMsg = VoiceChatMessage(
      sender: 'USER',
      text: promptText,
      timestamp: DateTime.now(),
      language: state.languageMode,
      attachedFishImage: attachedFishImage,
    );

    state = state.copyWith(
      messages: [...state.messages, userMsg],
      isQuerying: true,
    );

    final answer = await _voiceService.queryDrPauly(
      question: promptText,
      languageMode: state.languageMode,
      speciesContext: speciesContext,
      attachedFishImage: attachedFishImage,
    );

    final paulyMsg = VoiceChatMessage(
      sender: 'DR_PAULY',
      text: answer,
      timestamp: DateTime.now(),
      language: state.languageMode,
    );

    state = state.copyWith(
      messages: [...state.messages, paulyMsg],
      isQuerying: false,
    );

    // Trigger Speech Synthesis
    await _voiceService.speakText(answer, state.languageMode);
  }

  void stopAudio() {
    _voiceService.stopSpeech();
    state = state.copyWith(isSpeaking: false);
  }
}

final voiceAssistantProvider =
    StateNotifierProvider<VoiceAssistantNotifier, VoiceAssistantState>((ref) {
  return VoiceAssistantNotifier();
});
