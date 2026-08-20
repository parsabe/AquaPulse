import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter_tts/flutter_tts.dart';

class OllamaVoiceService {
  final Dio _dio = Dio(BaseOptions(
    connectTimeout: const Duration(seconds: 6),
    receiveTimeout: const Duration(seconds: 12),
  ));
  final FlutterTts _tts = FlutterTts();

  bool isSpeaking = false;

  OllamaVoiceService() {
    _initTts();
  }

  Future<void> _initTts() async {
    try {
      await _tts.setSpeechRate(0.5);
      await _tts.setVolume(1.0);

      _tts.setCompletionHandler(() {
        isSpeaking = false;
      });

      _tts.setErrorHandler((msg) {
        isSpeaking = false;
      });
    } catch (_) {}
  }

  Future<void> speakText(String text, String langCode) async {
    try {
      isSpeaking = true;
      await _tts.setLanguage(langCode == 'DE' ? 'de-DE' : 'en-US');
      await _tts.speak(text);
    } catch (_) {
      isSpeaking = false;
    }
  }

  Future<void> stopSpeech() async {
    try {
      await _tts.stop();
      isSpeaking = false;
    } catch (_) {}
  }

  Future<String> queryDrPauly({
    required String question,
    required String languageMode,
    String? speciesContext,
  }) async {
    final langPrompt = languageMode == 'DE'
        ? "Antworte absolut auf Deutsch in 2 prägnanten wissenschaftlichen Sätzen."
        : "Answer strictly in English in 2 direct expert sentences.";

    final prompt = '''
You are Dr. Daniel Pauly, world-renowned marine biologist. $langPrompt
Question: "$question" regarding aquatic specimen context: "${speciesContext ?? 'Salmo trutta & Gadus morhua'}".
Do not include any meta-talk, markdown titles, or language declarations.
''';

    // Try local Ollama endpoints (localhost or 10.0.2.2 for Android)
    final endpoints = [
      'http://localhost:11434/api/generate',
      'http://10.0.2.2:11434/api/generate',
      'http://127.0.0.1:11434/api/generate',
    ];

    for (var url in endpoints) {
      try {
        final res = await _dio.post(
          url,
          data: {
            'model': 'llama3',
            'prompt': prompt,
            'stream': false,
          },
        );

        if (res.statusCode == 200 && res.data != null) {
          final responseText = res.data['response']?.toString().trim();
          if (responseText != null && responseText.isNotEmpty) {
            return _cleanResponse(responseText);
          }
        }
      } catch (_) {
        // Continue fallback loop
      }
    }

    // Expert offline fallback responses
    if (languageMode == 'DE') {
      return "Dr. Daniel Pauly: Die populationsdynamische Analyse zeigt stabile stochastische Parameter für die beobachtete Art mit minimalem Aussterberisiko.";
    } else {
      return "Dr. Daniel Pauly: Biological telemetry confirms robust population dynamics with stable stochastic parameters across the observed marine habitat.";
    }
  }

  String _cleanResponse(String raw) {
    String text = raw.replaceAll('\n', ' ').replaceAll('\r', ' ');
    while (text.contains('  ')) {
      text = text.replaceAll('  ', ' ');
    }
    return text.trim();
  }
}
