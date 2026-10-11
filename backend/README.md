# QORGO API

Django + Django REST Framework. Локальные постоянные данные находятся в `qorgo.sqlite3` (не включать в Git).

## Запуск

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver 127.0.0.1:8000 --noreload
```

Во втором терминале:

```sh
.venv/bin/python manage.py process_safety
```

Worker проверяет таймеры и очередь каждые 2 секунды. Он должен работать постоянно; закрытие приложения не мешает обработке таймера, остановка сервера или worker мешает.

Тесты: `.venv/bin/python manage.py test safety`.

## Настройка отправки

Пример имён переменных: `.env.example`. Приложение читает переменные окружения; файл `.env` автоматически не загружается.

- SMS: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM.
- Email: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM, SMTP_TLS.

Без провайдера сообщения получают статус `unconfigured`. Twilio имеет приоритет над SMTP. SMS/SMTP acceptance не является подтверждением доставки.

## API

JSON. Авторизация: `Authorization: Token …`.

- POST `/api/register/`, POST `/api/login/`: email, password; register дополнительно name.
- POST `/api/logout/`: отзыв токена.
- GET/PATCH `/api/profile/`: имя и email; email в MVP неизменяемый.
- GET `/api/capabilities/`: настроены ли SMS/email.
- GET/POST `/api/contacts/`, PATCH/DELETE `/api/contacts/{id}/`.
- GET/POST `/api/alerts/`, GET `/api/alerts/{id}/`, POST resolve/retry.
- GET/POST `/api/journeys/`, POST `/api/journeys/{id}/arrive/` или cancel.

SOS принимает request_id UUID, необязательные latitude/longitude, location_at, location_accuracy. Один UUID у одного владельца создаёт одну тревогу. Данные другого пользователя не доступны.

## Публичный сервер

`runserver` предназначен для разработки. Не публиковать его через Cloudflare Tunnel. Для публикации подготовить отдельный сервер с HTTPS, WSGI/ASGI, приватным DJANGO_SECRET_KEY и DJANGO_DEBUG=0, постоянным worker, резервными копиями и ограничением нагрузки. DNS домена `qorgo.service` пока не изменён.
