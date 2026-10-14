import 'package:flutter/foundation.dart';

abstract class ViewModel extends ChangeNotifier {
  bool disposed = false;
  void notifyState() {
    if (!disposed) notifyListeners();
  }

  @override
  void dispose() {
    disposed = true;
    super.dispose();
  }
}
