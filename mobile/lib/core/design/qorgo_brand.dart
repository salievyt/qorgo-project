import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

class QorgoBrand extends StatelessWidget {
  const QorgoBrand({super.key, this.size = 31, this.center = false});
  final double size;
  final bool center;
  @override
  Widget build(BuildContext context) => Row(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment:
            center ? MainAxisAlignment.center : MainAxisAlignment.start,
        children: [
          SvgPicture.asset('assets/brand/qorgo-dark.svg',
              width: size * 1.1, height: size * 1.3),
          const SizedBox(width: 2),
          Text('QORGO',
              style: TextStyle(
                  fontFamily: 'Onest',
                  fontSize: size,
                  fontWeight: FontWeight.w500,
                  letterSpacing: -1.5)),
        ],
      );
}
