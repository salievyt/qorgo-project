import 'package:flutter/material.dart';
import '../design/qorgo_theme.dart';

class SosSlider extends StatefulWidget {
  const SosSlider({super.key, required this.onActivate, this.enabled = true});
  final VoidCallback onActivate;
  final bool enabled;
  @override
  State<SosSlider> createState() => _SosSliderState();
}

class _SosSliderState extends State<SosSlider> {
  double _position = 0;
  bool _activated = false;
  @override
  void didUpdateWidget(covariant SosSlider oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.enabled && !oldWidget.enabled) {
      _position = 0;
      _activated = false;
    }
  }

  void _reset() {
    if (!_activated && mounted) setState(() => _position = 0);
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(
        builder: (context, constraints) {
          final travel = constraints.maxWidth - 80;
          return Semantics(
            label: 'SOS. Потяните круг вправо до конца',
            child: Container(
              height: 80,
              decoration: BoxDecoration(
                color: widget.enabled ? QorgoDesign.danger : QorgoDesign.soft,
                borderRadius: BorderRadius.circular(40),
              ),
              child: Stack(
                children: [
                  const Positioned.fill(
                    child: Center(
                      child: Padding(
                        padding: EdgeInsets.only(left: 48),
                        child: Text(
                          'ПОТЯНИТЕ  › › ›',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.5,
                          ),
                        ),
                      ),
                    ),
                  ),
                  Positioned(
                    left: 8 + _position,
                    top: 8,
                    child: GestureDetector(
                      onHorizontalDragUpdate: widget.enabled
                          ? (details) {
                              if (_activated || travel <= 0) return;
                              setState(
                                () => _position = (_position + details.delta.dx)
                                    .clamp(0.0, travel),
                              );
                              if (_position >= travel) {
                                _activated = true;
                                widget.onActivate();
                              }
                            }
                          : null,
                      onHorizontalDragEnd: (_) => _reset(),
                      onHorizontalDragCancel: _reset,
                      child: Container(
                        key: const Key('sos-thumb'),
                        width: 64,
                        height: 64,
                        alignment: Alignment.center,
                        decoration: const BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                        ),
                        child: const Text(
                          'SOS',
                          style: TextStyle(
                            color: QorgoDesign.danger,
                            fontSize: 20,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      );
}
