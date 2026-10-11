# QORGO API

Единый Django-проект в `backend/`: мобильный MVP и расширенный API используют одну модель пользователя `accounts.User` и одну базу данных. Папка `qorgo_backend/` объединена с этим проектом.

## Локальный запуск

Из папки `backend/`:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver 127.0.0.1:8000 --noreload
```

Настройки читают окружение и `.env`. По умолчанию используется SQLite `unified.sqlite3`. Для PostgreSQL задайте `DB_ENGINE=django.db.backends.postgresql`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.

В отдельном терминале запустите один worker для таймеров и отправки сообщений мобильного MVP:

```sh
.venv/bin/python manage.py process_safety
```

Он проверяет очередь каждые 2 секунды. Закрытие мобильного приложения не мешает обработке таймера; остановка сервера или worker мешает. Расширенные задачи `/api/v1/` используют Celery и Redis:

```sh
.venv/bin/celery -A qorgo worker -l info
.venv/bin/celery -A qorgo beat -l info
```

Для WebSocket нужен Redis и ASGI-сервер: `.venv/bin/daphne -b 127.0.0.1 -p 8001 qorgo.asgi:application`.

## Перенос прежней базы MVP

Исходный `qorgo.sqlite3` сохранён без изменений и не используется как новая база: в нём другой тип идентификатора пользователя. После миграций импортируйте его в пустую новую базу:

```sh
.venv/bin/python manage.py import_legacy_backend qorgo.sqlite3
```

Импорт переносит пользователей, хеши паролей, действующие Token-токены, контакты, тревоги, статусы доставки и сопровождения с сохранением связей и дат. Пользователи получают UUID; аккаунты, зарегистрированные по email, могут не иметь телефона. Импорт выполняется атомарно и отказывается работать с непустой целевой базой, чтобы не перезаписать данные. Повторный импорт не нужен. Существующая PostgreSQL-база расширенного проекта обновляется обычной командой `migrate`; автоматическое объединение двух непустых баз не выполняется.

## Авторизация и совместимость

- `/api/` сохраняет контракты Flutter MVP: email/password, `Authorization: Token …`, списки без пагинации и прежние ошибки.
- `/api/v1/` сохраняет регистрацию и вход по телефону, `Authorization: Bearer …`, JWT, пагинацию и расширенные функции: семьи, SOS, геолокацию, геозоны, таймеры, уведомления, подписки и аналитику.
- Обе версии работают с одной моделью пользователя. Контакты, тревоги и таймеры разных версий сохраняют собственные модели и контракты.
- `/admin/` — админ-панель Jazzmin с оформлением QORGO и ссылками на документацию.
- `/api/docs/` и `/api/swagger/` — Swagger UI; `/api/redoc/` — ReDoc; `/api/schema/` — OpenAPI.
- В Swagger нажмите **Authorize**: для `/api/` используйте `Token <токен>`, для `/api/v1/` — JWT access token (Bearer). Документация доступна без входа; защищённые API требуют авторизации.
- Swagger/ReDoc используют локальные статические ресурсы. При развёртывании выполните `python manage.py collectstatic --noinput` и настройте обслуживание `/static/` (в Docker это делает Nginx).
- Создание администратора: `.venv/bin/python manage.py createsuperuser`.

## Настройка отправки MVP

- SMS: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM` (или `TWILIO_FROM_NUMBER`).
- Email: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_TLS`.

Без провайдера сообщения получают статус `unconfigured`. Twilio имеет приоритет над SMTP. Принятие сообщения провайдером не является подтверждением доставки. Настройки FCM, Vonage и SMS расширенного API также находятся в `.env.example`.

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

## Проверка

```sh
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python -m pytest
```

Тесты используют отдельную SQLite-базу в памяти и не требуют работающего Redis. `requirements-lock.txt` фиксирует проверенное окружение, включая зависимости тестов.

## Docker

```sh
cp .env.example .env
docker compose up --build
```

Compose включает PostgreSQL, Redis, HTTP API, ASGI, Celery, Celery Beat, отдельный worker MVP и Nginx. Для контейнеров адреса базы и Redis задаются именами сервисов. Перед публичным запуском задайте приватный `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, разрешённые хосты, HTTPS и резервное копирование. `runserver` предназначен для локальной разработки.
