import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // Brand Colors & Constants
  static const Color bgDark = Color(0xFF0F172A); // Deep Slate Navy
  static const Color bgCard = Color(0xFF1E293B); // Slate Dark Card
  static const Color bgSurface = Color(0xFF1E293B);
  
  // Neon Cyber Accents
  static const Color cyanAccent = Color(0xFF00F0FF); // Neon Cyan Reticle / Primary
  static const Color cyanSecondary = Color(0xFF06B6D4);
  static const Color goldAccent = Color(0xFFF59E0B); // Cyber Gold Highlight
  static const Color emeraldAccent = Color(0xFF10B981); // Normal / Healthy Status
  static const Color crimsonAccent = Color(0xFFEF4444); // Extinction / Risk Alarm
  static const Color violetAccent = Color(0xFFA855F7); // Neural SDE forecasting
  static const Color blueAccent = Color(0xFF3B82F6);

  // Text Colors
  static const Color textPrimary = Color(0xFFF8FAFC);
  static const Color textSecondary = Color(0xFF94A3B8);
  static const Color textMuted = Color(0xFF64748B);

  // Glassmorphism Constants
  static const double glassBlur = 16.0;
  static const double borderRadius = 16.0;

  static ThemeData get darkTheme {
    return ThemeData.dark(useMaterial3: true).copyWith(
      scaffoldBackgroundColor: bgDark,
      primaryColor: cyanAccent,
      colorScheme: const ColorScheme.dark(
        primary: cyanAccent,
        secondary: goldAccent,
        surface: bgSurface,
        background: bgDark,
        error: crimsonAccent,
        onPrimary: Colors.black,
        onSurface: textPrimary,
      ),
      textTheme: GoogleFonts.outfitTextTheme(ThemeData.dark().textTheme).copyWith(
        displayLarge: GoogleFonts.outfit(color: textPrimary, fontWeight: FontWeight.bold, fontSize: 32),
        titleLarge: GoogleFonts.outfit(color: textPrimary, fontWeight: FontWeight.w700, fontSize: 20),
        titleMedium: GoogleFonts.outfit(color: textPrimary, fontWeight: FontWeight.w600, fontSize: 16),
        bodyLarge: GoogleFonts.outfit(color: textPrimary, fontSize: 14),
        bodyMedium: GoogleFonts.outfit(color: textSecondary, fontSize: 12),
        labelSmall: GoogleFonts.jetBrainsMono(color: cyanAccent, fontSize: 11, fontWeight: FontWeight.w500),
      ),
      cardTheme: CardThemeData(
        color: bgCard.withOpacity(0.65),
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(borderRadius),
          side: BorderSide(color: cyanAccent.withOpacity(0.2), width: 1),
        ),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: bgDark,
        selectedItemColor: cyanAccent,
        unselectedItemColor: textMuted,
        type: BottomNavigationBarType.fixed,
        elevation: 10,
      ),
    );
  }
}
