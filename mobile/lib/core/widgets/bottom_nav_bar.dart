import 'package:flutter/material.dart';
import '../design/qorgo_theme.dart';

class QorgoBottomNavBar extends StatelessWidget {
  const QorgoBottomNavBar(
      {super.key, required this.selectedIndex, required this.onSelected});
  final int selectedIndex;
  final ValueChanged<int> onSelected;

  @override
  Widget build(BuildContext context) => DecoratedBox(
        decoration: const BoxDecoration(
            color: QorgoDesign.soft,
            border:
                Border(top: BorderSide(color: QorgoDesign.border, width: 0.5))),
        child: BottomNavigationBar(
          currentIndex: selectedIndex,
          onTap: onSelected,
          type: BottomNavigationBarType.fixed,
          backgroundColor: QorgoDesign.soft,
          elevation: 0,
          iconSize: 25,
          selectedItemColor: QorgoDesign.accent,
          unselectedItemColor: QorgoDesign.muted,
          selectedFontSize: 11,
          unselectedFontSize: 11,
          selectedLabelStyle: const TextStyle(fontWeight: FontWeight.w600),
          unselectedLabelStyle: const TextStyle(fontWeight: FontWeight.w400),
          showSelectedLabels: true,
          showUnselectedLabels: true,
          enableFeedback: true,
          items: const [
            BottomNavigationBarItem(
                icon: Icon(Icons.home_outlined),
                activeIcon: Icon(Icons.home_rounded),
                label: 'Главная'),
            BottomNavigationBarItem(
                icon: Icon(Icons.people_outline),
                activeIcon: Icon(Icons.people_rounded),
                label: 'Близкие'),
            BottomNavigationBarItem(
                icon: Icon(Icons.history_outlined),
                activeIcon: Icon(Icons.history_rounded),
                label: 'События'),
            BottomNavigationBarItem(
                icon: Icon(Icons.person_outline),
                activeIcon: Icon(Icons.person_rounded),
                label: 'Профиль'),
          ],
        ),
      );
}
