import 'dart:ui';
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class GlassContainer extends StatelessWidget {
  final Widget child;
  final double? width;
  final double? height;
  final EdgeInsetsGeometry padding;
  final EdgeInsetsGeometry margin;
  final Color? borderColor;
  final Color? backgroundColor;
  final double borderRadius;
  final double blur;
  final VoidCallback? onTap;

  const GlassContainer({
    Key? key,
    required this.child,
    this.width,
    this.height,
    this.padding = const EdgeInsets.all(16),
    this.margin = const EdgeInsets.all(0),
    this.borderColor,
    this.backgroundColor,
    this.borderRadius = 16.0,
    this.blur = 8.0,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final effectiveBg = (backgroundColor ?? AppTheme.bgCard).withOpacity(0.88);
    final effectiveBorder = (borderColor ?? AppTheme.cyanAccent).withOpacity(0.35);

    Widget innerCard = Container(
      padding: padding,
      decoration: BoxDecoration(
        color: effectiveBg,
        borderRadius: BorderRadius.circular(borderRadius),
        border: Border.all(
          color: effectiveBorder,
          width: 1.2,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.4),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
          BoxShadow(
            color: (borderColor ?? AppTheme.cyanAccent).withOpacity(0.08),
            blurRadius: 16,
          ),
        ],
      ),
      child: child,
    );

    Widget content = Container(
      width: width,
      height: height,
      margin: margin,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(borderRadius),
        child: blur > 0
            ? BackdropFilter(
                filter: ImageFilter.blur(sigmaX: blur, sigmaY: blur),
                child: innerCard,
              )
            : innerCard,
      ),
    );

    if (onTap != null) {
      return GestureDetector(
        onTap: onTap,
        child: content,
      );
    }
    return content;
  }
}
