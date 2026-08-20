import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';
import '../widgets/johnny_glitch_overlay.dart';
import 'live_camera_viewer_screen.dart';
import 'offline_taxonomy_screen.dart';
import 'ecological_risk_alarm_screen.dart';
import 'acousto_visual_sde_screen.dart';
import 'dr_pauly_voice_portal_screen.dart';
import 'profile_reports_screen.dart';

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
    ProfileReportsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return JohnnyGlitchOverlay(
      child: Scaffold(
        body: IndexedStack(index: _currentIndex, children: _screens),

        // SLEEK FLOATING JOHNNY SILVERHAND RELIC TRIGGER BUTTON [J]
        floatingActionButton: Builder(
          builder: (context) {
            return FloatingActionButton.extended(
              heroTag: "johnny_relic_fab",
              backgroundColor: const Color(0xFFDE52AF),
              elevation: 8,
              icon: const Icon(
                Icons.developer_board,
                color: Colors.white,
                size: 18,
              ),
              label: Text(
                "JOHNNY [J]",
                style: GoogleFonts.jetBrainsMono(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 10,
                  letterSpacing: 1.0,
                ),
              ),
              onPressed: () {
                JohnnyGlitchOverlay.of(context)?.triggerJohnnyRelicGlitch();
              },
            );
          },
        ),

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
              fontSize: 9,
              fontWeight: FontWeight.bold,
            ),
            unselectedLabelStyle: GoogleFonts.jetBrainsMono(fontSize: 8),
            type: BottomNavigationBarType.fixed,
            items: const [
              BottomNavigationBarItem(
                icon: Icon(Icons.videocam_outlined),
                activeIcon: Icon(Icons.videocam, color: AppTheme.cyanAccent),
                label: 'STREAM',
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
                label: 'ALARMS',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.equalizer_outlined),
                activeIcon: Icon(Icons.equalizer, color: AppTheme.cyanAccent),
                label: 'SDE',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.mic_none_outlined),
                activeIcon: Icon(Icons.mic, color: AppTheme.violetAccent),
                label: 'DR. PAULY',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.person_outline),
                activeIcon: Icon(Icons.person, color: AppTheme.cyanAccent),
                label: 'PROFILE',
              ),
            ],
          ),
        ),
      ),
    );
  }
}
