import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/services.dart';

class AlarmSoundService {
  final AudioPlayer _audioPlayer = AudioPlayer();
  DateTime _lastAlarmTime = DateTime.now().subtract(const Duration(seconds: 10));

  Future<void> triggerEcologicalAlarm({
    required double extinctionRisk,
    required double bifurcationIndex,
  }) async {
    // Prevent spamming alarm sound more than once every 4 seconds
    if (DateTime.now().difference(_lastAlarmTime).inSeconds < 4) return;
    _lastAlarmTime = DateTime.now();

    // Haptic feedback alert
    try {
      HapticFeedback.heavyImpact();
    } catch (_) {}

    // Synthesize warning alert tones using AudioPlayer
    try {
      if (extinctionRisk > 50.0 || bifurcationIndex > 70.0) {
        // High severity dual alert tone
        await _audioPlayer.play(AssetSource('audio/critical_alarm.mp3'));
      } else {
        await _audioPlayer.play(AssetSource('audio/warning_beep.mp3'));
      }
    } catch (_) {
      // System fallback beep if asset sound is unavailable
      try {
        SystemSound.play(SystemSoundType.alert);
      } catch (_) {}
    }
  }

  void stopAlarm() {
    try {
      _audioPlayer.stop();
    } catch (_) {}
  }
}
