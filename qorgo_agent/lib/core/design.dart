import 'package:flutter/material.dart';

abstract final class AgentDesign {
  static const background = Color(0xFF030705);
  static const surface = Color(0xFF111513);
  static const border = Color(0xFF254331);
  static const text = Color(0xFFF2F7F3);
  static const muted = Color(0xFF8CAA97);
  static const green = Color(0xFF235D3B);
  static const accent = Color(0xFFA0CEAE);
  static const danger = Color(0xFFD34C43);

  static ThemeData get theme => ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    scaffoldBackgroundColor: background,
    fontFamily: 'Onest',
    fontFamilyFallback: const ['OnestCyrillic'],
    colorScheme: const ColorScheme.dark(
      primary: accent,
      surface: surface,
      onSurface: text,
      error: danger,
    ),
    cardTheme: CardThemeData(
      color: surface,
      elevation: 0,
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: const BorderSide(color: border),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: surface,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: border),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: green,
        foregroundColor: Colors.white,
        minimumSize: const Size(0, 52),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    ),
  );
}
