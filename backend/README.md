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

## Vercel и PostgreSQL

Проект Vercel: `qorgo-project-backend`, корневая папка `backend/`. Основной адрес: `https://api.qorgo.services`. `vercel.json` выбирает Django и запускает `build.py` перед публикацией; точка входа определяется через `manage.py` и настройки проекта. Vercel собирает статические ресурсы Swagger и Jazzmin автоматически.

Для production задайте в Vercel:

- `DATABASE_URL` — строка подключения PostgreSQL от Neon; при наличии `DATABASE_URL_UNPOOLED` миграции используют прямое подключение.
- `DJANGO_SECRET_KEY` — приватный случайный ключ.
- `DJANGO_DEBUG=False`.
- `DJANGO_ALLOWED_HOSTS=api.qorgo.services,qorgo-project-backend.vercel.app`.
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://api.qorgo.services,https://qorgo-project-backend.vercel.app`.

В Vercel SQLite запрещена: без `DATABASE_URL` приложение не запустится. `build.py` применяет миграции до публикации. Мобильные аккаунты продолжают входить по телефону/email; администраторы дополнительно могут иметь уникальный `username` и входить с ним на `/admin/`.

Для первоначального администратора задайте `BOOTSTRAP_ADMIN_USERNAME`, `BOOTSTRAP_ADMIN_EMAIL`, `BOOTSTRAP_ADMIN_PASSWORD` как production-секреты. После успешного создания удалите эти переменные. Команда `.venv/bin/python manage.py bootstrap_admin` создаёт аккаунт один раз и не сбрасывает существующий пароль или права другого пользователя. Пароли и строки подключения не включаются в исходники.

HTTP API и админ-панель развёртываются на Vercel. Постоянные процессы `process_safety`, Celery Worker/Beat должны работать на отдельном сервере; публикация HTTP API сама по себе не запускает их. Локальные медиафайлы также требуют постоянного внешнего хранилища для production.

### Контент лендинга

В Jazzmin доступен раздел «Контент лендинга»: тексты (по разделам и поиску),
ссылки, файлы, FAQ, тарифы и документы. Новые документы по умолчанию из начальной
миграции сохранены как черновики — включите «Показывать» после проверки.
Для замены презентации загрузите файл и выберите его в ссылке «Презентация QORGO».
Файлы до 4 МБ сохраняются в PostgreSQL, доступны публично для скачивания и
сохраняются между деплоями. Загружайте только материалы для публикации.

Публичный API: `/api/v1/content/`. Лендинг загружает контент при открытии;
изменения из админки не требуют пуша или пересборки. Если API недоступен,
сохраняется встроенный контент. `VITE_CONTENT_API_URL` позволяет сменить адрес API.

Каждый push в `main` запускает production deployment через Git-интеграцию Vercel.
`backend/vercel.json` запускает `build.py`, который сначала применяет все
неприменённые миграции через прямое подключение PostgreSQL. При ошибке миграции
сборка завершается ошибкой. Для изменений моделей создайте и закоммитьте файлы
миграций заранее; production не создаёт их автоматически. Используйте совместимые
со старой версией изменения схемы, поскольку предыдущая версия обслуживает запросы
во время сборки. Начальный контент добавляется одной миграцией и не перезаписывается
на следующих пушах.

### SOS между аккаунтами мобильного MVP

Контакт с email зарегистрированного аккаунта получает SOS в `GET /api/inbox/` без внешнего провайдера и фонового worker. `POST /api/inbox/{delivery_id}/acknowledge/` подтверждает помощь; отправитель видит статус `received` и канал `app`. Статус `available` означает наличие сигнала в аккаунте, а не получение человеком. Доступ проверяется по email текущего авторизованного пользователя; чужие подтверждения и завершение тревог запрещены. На закрытом приложении push пока не реализован. При отправке на зарегистрированный аккаунт приоритет имеет доставка в QORGO; внешняя SMS/email-рассылка для этой записи не запускается.


### Добавление близкого по номеру

- `GET/PATCH /api/profile/`: `phone_number` в международном формате; поле можно оставить пустым. Номер уникален; SMS-подтверждение пока отсутствует.
- `POST /api/contacts/lookup/`: один `phone`, точное совпадение активного аккаунта; возвращаются `registered`, нормализованный номер, отображаемое имя и `already_added`. Email и UUID друга не возвращаются. Token обязателен, до 30 запросов в минуту.
- `POST /api/contacts/`: `link_registered=true` проверяет аккаунт по номеру и сохраняет связь. `in_qorgo` — поле ответа.
- Contact/Delivery используют nullable `recipient` на модель пользователя; новые SOS приходят в inbox по этой связи, независимо от изменения email/номера получателя. Старые email-доставки совместимы.
- Миграция `0003_link_existing_phone_contacts` связывает старые контакты с активными аккаунтами по точному номеру, сохраняя ограничения от дублей; история тревог не переназначается.
