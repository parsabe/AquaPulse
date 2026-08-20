import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';
import 'live_camera_viewer_screen.dart';
import 'offline_taxonomy_screen.dart';
import 'ecological_risk_alarm_screen.dart';
import 'acousto_visual_sde_screen.dart';
import 'dr_pauly_voice_portal_screen.dart';

class MainNavigationScreen extends ConsumerStatefulWidget {
  const MainNavigationScreen({super.key});

  @override
  ConsumerState<MainNavigationScreen> createState() =>
      _MainNavigationScreenState();
}

class _MainNavigationScreenState extends ConsumerState<MainNavigationScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    LiveCameraViewerScreen(),
    OfflineTaxonomyScreen(),
    EcologicalRiskAlarmScreen(),
    AcoustoVisualSdeScreen(),
    DrPaulyVoicePortalScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _currentIndex, children: _screens),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: AppTheme.bgDark,
          border: Border(
            top: BorderSide(
              color: AppTheme.cyanAccent.withValues(alpha: 0.2),
              width: 1,
            ),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.5),
              blurRadius: 16,
              offset: const Offset(0, -4),
            ),
          ],
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) {
            setState(() {
              _currentIndex = index;
            });
          },
          backgroundColor: Colors.transparent,
          selectedItemColor: AppTheme.cyanAccent,
          unselectedItemColor: AppTheme.textMuted,
          selectedLabelStyle: GoogleFonts.jetBrainsMono(
            fontSize: 10,
            fontWeight: FontWeight.bold,
          ),
          unselectedLabelStyle: GoogleFonts.jetBrainsMono(fontSize: 9),
          type: BottomNavigationBarType.fixed,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.videocam_outlined),
              activeIcon: Icon(Icons.videocam, color: AppTheme.cyanAccent),
              label: 'LIVE STREAM',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.storage_outlined),
              activeIcon: Icon(Icons.storage, color: AppTheme.cyanAccent),
              label: 'TAXONOMY',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.warning_amber_outlined),
              activeIcon: Icon(
                Icons.warning_amber_rounded,
                color: AppTheme.crimsonAccent,
              ),
              label: 'RISK ALARMS',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.equalizer_outlined),
              activeIcon: Icon(Icons.equalizer, color: AppTheme.cyanAccent),
              label: 'ACOUSTO/SDE',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.mic_none_outlined),
              activeIcon: Icon(Icons.mic, color: AppTheme.violetAccent),
              label: 'DR. PAULY',
            ),
          ],
        ),
      ),
    );
  }
}
