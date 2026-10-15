import 'package:flutter/material.dart';

/// Tokens copied from landing/src/styles.css; sizes adapted for touch screens.
abstract final class QorgoDesign {
  static const accent = Color(0xFFA0CEAE);
  static const green = Color(0xFF235D3B);
  static const ink = Color(0xFFF2F7F3);
  static const muted = Color(0xFF8CAA97);
  static const background = Color(0xFF030705);
  static const soft = Color(0xFF111513);
  static const border = Color(0xFF254331);
  static const danger = Color(0xFFD34C43);

  static ThemeData get theme {
    final scheme =
        ColorScheme.fromSeed(seedColor: green, brightness: Brightness.dark)
            .copyWith(
      primary: accent,
      onPrimary: Colors.white,
      surface: soft,
      onSurface: ink,
      onSurfaceVariant: muted,
      error: danger,
      outline: border,
      secondary: accent,
      surfaceTint: Colors.transparent,
    );
    final base = ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
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
          color: soft,
          surfaceTintColor: Colors.transparent,
          elevation: 0,
          margin: const EdgeInsets.only(bottom: 12),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(24))),
      inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: soft,
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
              borderSide: const BorderSide(color: accent, width: 1.5))),
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
              foregroundColor: accent,
              shape: shape,
              textStyle: const TextStyle(
                  fontFamily: 'Onest',
                  fontFamilyFallback: ['OnestCyrillic'],
                  fontSize: 14,
                  fontWeight: FontWeight.w600))),
      navigationBarTheme: NavigationBarThemeData(
          backgroundColor: soft,
          surfaceTintColor: Colors.transparent,
          elevation: 0,
          height: 72,
          indicatorColor: const Color(0xFF205138),
          labelTextStyle: WidgetStateProperty.resolveWith((states) => TextStyle(
              fontFamily: 'Onest',
              fontFamilyFallback: const ['OnestCyrillic'],
              fontSize: 11,
              color: states.contains(WidgetState.selected) ? accent : muted,
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
          backgroundColor: soft,
          surfaceTintColor: Colors.transparent,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(24))),
      dividerTheme: const DividerThemeData(color: border, thickness: 1),
    );
  }
}
