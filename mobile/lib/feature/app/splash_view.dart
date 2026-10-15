import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../../core/design/qorgo_theme.dart';

class SplashView extends StatelessWidget {
  const SplashView({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(
        body: SafeArea(
            child: Center(
                child: TweenAnimationBuilder<double>(
          tween: Tween(begin: 0, end: 1),
          duration: MediaQuery.disableAnimationsOf(context)
              ? Duration.zero
              : const Duration(milliseconds: 600),
          builder: (context, value, child) => Opacity(
              opacity: value,
              child: Transform.translate(
                  offset: Offset(0, 8 * (1 - value)), child: child)),
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            SizedBox(
                width: 248,
                height: 248,
                child: Stack(alignment: Alignment.center, children: [
                  for (final size in [248.0, 188.0, 128.0])
                    Container(
                        width: size,
                        height: size,
                        decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: size == 128 ? const Color(0x18205138) : null,
                            border:
                                Border.all(color: const Color(0x453D775C)))),
                  SvgPicture.asset('assets/brand/qorgo-light.svg',
                      width: 88, height: 110),
                ])),
            const SizedBox(height: 28),
            const Text('QORGO',
                style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 2)),
            const SizedBox(height: 8),
            const Text('Ваш круг безопасности',
                style: TextStyle(fontSize: 13, color: QorgoDesign.muted)),
            const SizedBox(height: 36),
            const SizedBox(
                width: 18,
                height: 18,
                child: CircularProgressIndicator(
                    strokeWidth: 1.5, color: QorgoDesign.accent)),
          ]),
        ))),
      );
}
