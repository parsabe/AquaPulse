import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/specimen_model.dart';
import '../models/taxonomy_model.dart';
import '../models/telemetry_data_point.dart';
import '../services/database_service.dart';
import '../services/gbif_api_service.dart';
import '../services/telemetry_engine_service.dart';
import '../services/ollama_voice_service.dart';
import '../services/alarm_sound_service.dart';

// --- TELEMETRY STATE & PROVIDER ---
class TelemetryState {
  final TelemetryDataPoint currentPoint;
  final List<TelemetryDataPoint> history;
  final List<SpecimenModel> liveSpecimens;
  final String activeShock;
  final bool isSimulating;
  final double streamFps;

  TelemetryState({
    required this.currentPoint,
    required this.history,
    required this.liveSpecimens,
    required this.activeShock,
    this.isSimulating = true,
    this.streamFps = 29.8,
  });

  TelemetryState copyWith({
    TelemetryDataPoint? currentPoint,
    List<TelemetryDataPoint>? history,
    List<SpecimenModel>? liveSpecimens,
    String? activeShock,
    bool? isSimulating,
    double? streamFps,
  }) {
    return TelemetryState(
      currentPoint: currentPoint ?? this.currentPoint,
      history: history ?? this.history,
      liveSpecimens: liveSpecimens ?? this.liveSpecimens,
      activeShock: activeShock ?? this.activeShock,
      isSimulating: isSimulating ?? this.isSimulating,
      streamFps: streamFps ?? this.streamFps,
    );
  }
}

class TelemetryNotifier extends StateNotifier<TelemetryState> {
  final TelemetryEngineService _engine = TelemetryEngineService();
  final AlarmSoundService _alarmSound = AlarmSoundService();
  Timer? _timer;

  TelemetryNotifier()
      : super(TelemetryState(
          currentPoint: TelemetryDataPoint(
            timeSec: 0,
            preyX: 10,
            predY: 5,
            extinctionRiskPct: 15.0,
            bifurcationIndexPct: 18.0,
            shannonH: 1.45,
            pielouJ: 0.78,
            kalmanGainX: 0.35,
            kalmanGainY: 0.18,
            innovationResidual: 0.1,
            velocityMagnitude: 4.5,
            covarianceTrace: 1.2,
            ecoRatioXY: 2.0,
            detectionFps: 29.8,
          ),
          history: [],
          liveSpecimens: [],
          activeShock: "NORMAL",
        )) {
    _startLoop();
  }

  void _startLoop() {
    _timer = Timer.periodic(const Duration(milliseconds: 600), (_) {
      if (!state.isSimulating) return;

      final point = _engine.step(yoloPreyObservation: 10.0);
      final specimens = _engine.generateLiveSpecimens();

      // Check Extinction Risk > 35% or Bifurcation Index > 50%
      if (point.extinctionRiskPct > 35.0 || point.bifurcationIndexPct > 50.0) {
        _alarmSound.triggerEcologicalAlarm(
          extinctionRisk: point.extinctionRiskPct,
          bifurcationIndex: point.bifurcationIndexPct,
        );
        DatabaseService.instance.logAlarmEvent(
          point.extinctionRiskPct > 35.0 ? "EXTINCTION_RISK" : "BIFURCATION_COLLAPSE",
          point.extinctionRiskPct,
          point.bifurcationIndexPct,
          "Threshold breach in remote telemetry stream",
        );
      }

      state = state.copyWith(
        currentPoint: point,
        history: List.from(_engine.history),
        liveSpecimens: specimens,
        activeShock: _engine.activeShock,
      );
    });
  }

  void triggerEnvironmentalShock(String shockType) {
    _engine.injectShock(shockType);
    state = state.copyWith(activeShock: _engine.activeShock);
  }

  void toggleSimulation() {
    state = state.copyWith(isSimulating: !state.isSimulating);
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }
}

final telemetryProvider = StateNotifierProvider<TelemetryNotifier, TelemetryState>((ref) {
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

final taxonomyProvider = StateNotifierProvider<TaxonomyNotifier, List<TaxonomyModel>>((ref) {
  return TaxonomyNotifier();
});


// --- VOICE ASSISTANT STATE & PROVIDER ---
class VoiceChatMessage {
  final String sender; // 'USER' or 'DR_PAULY'
  final String text;
  final DateTime timestamp;
  final String language;

  VoiceChatMessage({
    required this.sender,
    required this.text,
    required this.timestamp,
    required this.language,
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
              text: "Welcome to field telemetry portal. I am Dr. Paul Pauly. Ask any ecological or species question in English or German.",
              timestamp: DateTime.now(),
              language: 'EN',
            )
          ],
        ));

  void toggleLanguage() {
    final nextLang = state.languageMode == 'EN' ? 'DE' : 'EN';
    state = state.copyWith(languageMode: nextLang);
  }

  Future<void> sendQuery(String userQuestion, {String? speciesContext}) async {
    if (userQuestion.trim().isEmpty) return;

    final userMsg = VoiceChatMessage(
      sender: 'USER',
      text: userQuestion,
      timestamp: DateTime.now(),
      language: state.languageMode,
    );

    state = state.copyWith(
      messages: [...state.messages, userMsg],
      isQuerying: true,
    );

    final answer = await _voiceService.queryDrPauly(
      question: userQuestion,
      languageMode: state.languageMode,
      speciesContext: speciesContext,
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
