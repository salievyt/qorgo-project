# QORGO Mobile MVP

Flutter-приложение Android 10+ / iOS 15+ с чистой архитектурой. Рабочие данные хранятся на Django-сервере, токен — в защищённом хранилище телефона.

Функции: аккаунт, профиль, доверенные контакты, SOS с геопозицией, таймер прибытия и история. Системные SMS и звонки работают на физическом телефоне; iOS-симулятор может их не поддерживать.

## Запуск на iPhone-симуляторе

Сначала запустить API и worker по инструкции `../backend/README.md`.

```sh
/Users/sm1le/Development/flutter/bin/flutter pub get
/Users/sm1le/Development/flutter/bin/flutter run --dart-define=QORGO_API_URL=http://127.0.0.1:8000/api
```

В Xcode 27 iOS-симулятор открывается через Device Hub:
`/Applications/Xcode.app/Contents/Applications/DeviceHub.app`.

Создайте аккаунт в приложении; добавьте доверенный контакт; установите таймер или выполните полный жест SOS. Данные сохраняются между запусками. Автоматическая доставка требует Twilio/SMTP на сервере. Без провайдера интерфейс сообщает об отсутствии отправки.

Для физического телефона указать доступный с него HTTPS-адрес API. Release-сборка не допускает HTTP; не распространять debug-сборку с localhost как публичный MVP.

## Проверки

```sh
flutter analyze
flutter test
flutter build ios --simulator --debug
flutter build apk --debug
```

## Архитектура

`lib/domain`: сущности, контракты и сценарии без Flutter/HTTP.
`lib/data`: API, Keychain и платформенные реализации.
`lib/presentation`: экраны, формы и управление состоянием.
`lib/main.dart`: создание и связывание зависимостей.

Подробности: `../docs/architecture/Mobile_MVP.md`.

Полноценная групповая карта, push, OTP по телефону и доказательства не входят в эту итерацию. Домен qorgo.service существует, но публичный API на нём ещё не размещён.
