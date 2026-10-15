# QORGO AGENT

Отдельное рабочее приложение для сотрудников реагирования QORGO.

Оператор входит по выданному рабочему телефону и паролю, видит активную
очередь SOS, открывает координаты, принимает инцидент в работу и завершает
его с комментарием. Доступ к API есть только у аккаунтов с ролью
`emergency_operator`, `admin` или у суперпользователя.

```sh
/Users/sm1le/develop/flutter/bin/flutter pub get
/Users/sm1le/develop/flutter/bin/flutter run
```

По умолчанию используется `https://api.qorgo.services/api/v1`. Для локального
сервера: `--dart-define=QORGO_API_URL=http://127.0.0.1:8000/api/v1`.

## Getting Started

This project is a starting point for a Flutter application.

A few resources to get you started if this is your first Flutter project:

- [Learn Flutter](https://docs.flutter.dev/get-started/learn-flutter)
- [Write your first Flutter app](https://docs.flutter.dev/get-started/codelab)
- [Flutter learning resources](https://docs.flutter.dev/reference/learning-resources)

For help getting started with Flutter development, view the
[online documentation](https://docs.flutter.dev/), which offers tutorials,
samples, guidance on mobile development, and a full API reference.
