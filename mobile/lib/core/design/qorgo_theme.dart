import 'package:flutter/material.dart';

/// Tokens copied from landing/src/styles.css; sizes adapted for touch screens.
abstract final class QorgoDesign {
  static const green = Color(0xFF235D3B);
  static const ink = Color(0xFF080B09);
  static const muted = Color(0xFF5E6470);
  static const background = Color(0xFFEEF0F4);
  static const soft = Color(0xFFF6F7F9);
  static const border = Color(0xFFE0E4E8);
  static const danger = Color(0xFFD34C43);

  static ThemeData get theme {
    final scheme = ColorScheme.fromSeed(seedColor: green).copyWith(
      primary: green,
      onPrimary: Colors.white,
      surface: Colors.white,
      onSurface: ink,
      onSurfaceVariant: muted,
      error: danger,
      outline: border,
      secondary: green,
      surfaceTint: Colors.transparent,
    );
    final base = ThemeData(
        useMaterial3: true,
        fontFamily: 'Onest',
        fontFamilyFallback: const ['OnestCyrillic'],
        colorScheme: scheme);
    final shape =
        RoundedRectangleBorder(borderRadius: BorderRadius.circular(12));
    return base.copyWith(
      scaffoldBackgroundColor: background,
      textTheme: base.textTheme.apply(bodyColor: ink, displayColor: ink),
      appBarTheme: const AppBarTheme(
          backgroundColor: background,
          surfaceTintColor: Colors.transparent,
          elevation: 0,
          centerTitle: false,
          titleTextStyle: TextStyle(
              fontFamily: 'Onest',
              fontFamilyFallback: ['OnestCyrillic'],
              color: ink,
              fontSize: 24,
              fontWeight: FontWeight.w500,
              letterSpacing: -1.2)),
      cardTheme: CardThemeData(
          color: Colors.white,
          surfaceTintColor: Colors.transparent,
          elevation: 0,
          margin: const EdgeInsets.only(bottom: 12),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(24))),
      inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 16, vertical: 18),
          labelStyle: const TextStyle(color: muted, fontSize: 14),
          border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: border)),
          enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: border)),
          focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: green, width: 1.5))),
      filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
              backgroundColor: green,
              foregroundColor: Colors.white,
              minimumSize: const Size(0, 52),
              shape: shape,
              elevation: 0,
              textStyle: const TextStyle(
                  fontFamily: 'Onest',
                  fontFamilyFallback: ['OnestCyrillic'],
                  fontSize: 14,
                  fontWeight: FontWeight.w600))),
      outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(
              foregroundColor: ink,
              minimumSize: const Size(0, 52),
              shape: shape,
              side: const BorderSide(color: border))),
      textButtonTheme: TextButtonThemeData(
          style: TextButton.styleFrom(
              foregroundColor: green,
              shape: shape,
              textStyle: const TextStyle(
                  fontFamily: 'Onest',
                  fontFamilyFallback: ['OnestCyrillic'],
                  fontSize: 14,
                  fontWeight: FontWeight.w600))),
      navigationBarTheme: NavigationBarThemeData(
          backgroundColor: Colors.white,
          surfaceTintColor: Colors.transparent,
          elevation: 0,
          height: 72,
          indicatorColor: const Color(0xFFEAF2ED),
          labelTextStyle: WidgetStateProperty.resolveWith((states) => TextStyle(
              fontFamily: 'Onest',
              fontFamilyFallback: const ['OnestCyrillic'],
              fontSize: 11,
              color: states.contains(WidgetState.selected) ? green : muted,
              fontWeight: states.contains(WidgetState.selected)
                  ? FontWeight.w600
                  : FontWeight.w400))),
      bottomSheetTheme: const BottomSheetThemeData(
          backgroundColor: background,
          surfaceTintColor: Colors.transparent,
          showDragHandle: true,
          shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.vertical(top: Radius.circular(24)))),
      dialogTheme: DialogThemeData(
          backgroundColor: Colors.white,
          surfaceTintColor: Colors.transparent,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(24))),
      dividerTheme: const DividerThemeData(color: border, thickness: 1),
    );
  }
}
