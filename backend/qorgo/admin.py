from django.contrib import admin
from django.contrib.admin import AdminSite


APP_NAMES = {
    'content': 'Сайт и контент',
    'accounts': 'Пользователи',
    'sos': 'Тревоги SOS',
    'families': 'Семьи',
    'safety_timers': 'Сопровождение',
    'location': 'Местоположение',
    'geofences': 'Безопасные зоны',
    'subscriptions': 'Тарифы и подписки',
    'analytics': 'Отчёты',
    'notifications': 'Уведомления',
    'auth': 'Права доступа',
}

MODEL_NAMES = {
    'content.text': 'Тексты лендинга',
    'content.link': 'Ссылки лендинга',
    'content.asset': 'Файлы и изображения',
    'content.faq': 'Вопросы и ответы',
    'content.pricing': 'Цены и тарифы сайта',
    'content.document': 'Документы сайта',
    'accounts.user': 'Аккаунты',
    'accounts.emergencycontact': 'Доверенные контакты',
    'accounts.privacysettings': 'Настройки приватности',
    'accounts.deviceinfo': 'Устройства',
    'sos.alert': 'Сигналы SOS',
    'sos.evidencerecording': 'Записи и материалы SOS',
    'families.family': 'Семейные круги',
    'families.familymembership': 'Участники семей',
    'families.invitecode': 'Коды приглашения',
    'location.activelocation': 'Последнее местоположение',
    'location.locationupdate': 'История местоположений',
    'geofences.geofence': 'Безопасные зоны',
    'geofences.geofenceevent': 'События в зонах',
    'safety_timers.safetytimer': 'Таймеры сопровождения',
    'subscriptions.subscriptionplan': 'Планы подписок',
    'subscriptions.subscription': 'Подписки пользователей',
    'analytics.analyticsevent': 'События приложения',
    'analytics.dailyreport': 'Ежедневные отчёты',
    'auth.group': 'Группы доступа',
    'auth.permission': 'Разрешения',
}

FIELD_LABELS = {
    'username': 'Логин', 'phone_number': 'Телефон', 'email': 'Электронная почта',
    'first_name': 'Имя', 'last_name': 'Фамилия', 'name': 'Название', 'title': 'Название',
    'label': 'Подпись', 'key': 'Системный ключ', 'section': 'Раздел сайта',
    'value': 'Текст на сайте', 'url': 'Адрес ссылки', 'asset': 'Загруженный файл',
    'filename': 'Имя файла', 'upload': 'Выбрать файл', 'question': 'Вопрос',
    'answer': 'Ответ', 'position': 'Порядок на сайте', 'active': 'Показывать на сайте',
    'body': 'Содержание', 'slug': 'Короткий адрес', 'data': 'Данные',
    'user': 'Пользователь', 'created_by': 'Создал', 'created_at': 'Дата создания',
    'updated_at': 'Последнее изменение', 'timestamp': 'Дата и время',
    'date': 'Дата', 'status': 'Статус', 'role': 'Роль', 'is_active': 'Аккаунт активен',
    'is_staff': 'Доступ в админку', 'is_superuser': 'Полные права администратора',
    'is_premium': 'Premium', 'premium_expiry': 'Premium до', 'last_active_at': 'Последняя активность',
    'date_joined': 'Дата регистрации', 'last_login': 'Последний вход',
    'gender': 'Пол', 'city': 'Город', 'date_of_birth': 'Дата рождения',
    'photo': 'Фото', 'blood_type': 'Группа крови', 'medical_notes': 'Медицинская информация',
    'privacy_settings': 'Настройки приватности', 'devices': 'Устройства',
    'show_location': 'Показывать местоположение', 'location_visibility': 'Кому видно местоположение',
    'show_profile': 'Показывать профиль', 'share_battery_level': 'Делиться зарядом батареи',
    'share_speed': 'Делиться скоростью', 'platform': 'Платформа', 'device_model': 'Модель устройства',
    'os_version': 'Версия системы', 'app_version': 'Версия приложения',
    'battery_level': 'Заряд батареи, %', 'fcm_token': 'Токен уведомлений',
    'family': 'Семья', 'family_name': 'Название семьи', 'created_by_user': 'Создатель',
    'invite_code': 'Код приглашения', 'member_count': 'Участники', 'joined_at': 'Дата вступления',
    'is_used': 'Использован', 'used_by': 'Кто использовал', 'used_at': 'Дата использования',
    'latitude': 'Широта', 'longitude': 'Долгота', 'accuracy': 'Точность, м',
    'speed': 'Скорость, м/с', 'heading': 'Направление', 'is_background': 'Фоновое обновление',
    'is_stale': 'Данные устарели', 'last_updated': 'Последнее обновление',
    'zone_type': 'Тип зоны', 'radius': 'Радиус, м', 'event_type': 'Тип события',
    'destination_address': 'Куда направляется', 'estimated_arrival_at': 'Ожидаемое прибытие',
    'started_at': 'Начало', 'resolved_at': 'Завершено', 'resolved_by': 'Кто завершил',
    'trigger_method': 'Как поступил сигнал', 'address': 'Адрес', 'map_link': 'Ссылка на карту',
    'operator_note': 'Заметка оператора', 'assigned_operator': 'Ответственный оператор',
    'assigned_at': 'Когда назначен', 'notified_contacts': 'Оповещённые контакты',
    'family_notified': 'Семья оповещена', 'emergency_services_notified': 'Службы оповещены',
    'alert': 'Сигнал SOS', 'evidence_type': 'Тип записи', 'file': 'Файл',
    'duration_seconds': 'Длительность, сек.', 'file_size_bytes': 'Размер файла, байт',
    'mime_type': 'Формат файла', 'plan_type': 'Тип тарифа', 'plan': 'Тариф',
    'price_usd': 'Цена, USD', 'price_som': 'Цена, сом', 'max_family_members': 'Максимум участников семьи',
    'history_retention_days': 'История хранится, дней', 'expires_at': 'Действует до',
    'canceled_at': 'Дата отмены', 'auto_renew': 'Автопродление', 'payment_provider': 'Способ оплаты',
    'payment_provider_id': 'Номер платежа', 'event_name': 'Событие', 'session_id': 'Сессия',
    'parameters': 'Параметры', 'ip_address': 'IP-адрес', 'user_agent': 'Браузер или приложение',
    'total_users': 'Всего пользователей', 'new_users': 'Новые пользователи',
    'active_users': 'Активные пользователи', 'premium_users': 'Premium-пользователи',
    'sos_alerts_count': 'Сигналы SOS', 'active_alerts_count': 'Активные сигналы',
    'families_created': 'Создано семей', 'safety_timers_created': 'Таймеры сопровождения',
    'total_revenue_usd': 'Доход, USD', 'groups': 'Группы доступа', 'user_permissions': 'Разрешения пользователя',
}

FIELD_CHOICES = {
    'role': {
        'user': 'Пользователь', 'admin': 'Администратор', 'emergency_operator': 'Оператор тревог',
        'creator': 'Создатель семьи', 'parent': 'Родитель', 'child': 'Ребёнок',
        'spouse': 'Супруг или супруга', 'relative': 'Родственник', 'friend': 'Друг',
    },
    'status': {
        'active': 'Активна', 'resolved': 'Завершена', 'false_alarm': 'Ложная тревога',
        'expired': 'Время истекло', 'canceled': 'Отменена', 'cancelled': 'Отменена',
        'arrived': 'Прибыл', 'missed': 'Не прибыл', 'trial': 'Пробный период',
        'canceled': 'Отменена', 'expired': 'Истекла',
    },
    'trigger_method': {
        'sos_button': 'Кнопка SOS', 'widget': 'Виджет', 'power_button': 'Кнопка питания',
        'shake': 'Встряхивание', 'safety_timer': 'Таймер сопровождения', 'safety_ai': 'Анализ безопасности',
    },
    'gender': {'male': 'Мужской', 'female': 'Женский', 'other': 'Другой'},
    'location_visibility': {
        'family': 'Только семья', 'contacts': 'Доверенные контакты', 'nobody': 'Никому',
    },
    'platform': {'ios': 'iPhone (iOS)', 'android': 'Android'},
    'zone_type': {
        'home': 'Дом', 'school': 'Школа', 'university': 'Университет',
        'work': 'Работа', 'custom': 'Другое место',
    },
    'event_type': {'entry': 'Вход в зону', 'exit': 'Выход из зоны'},
    'evidence_type': {
        'audio': 'Аудиозапись', 'video_front': 'Видео с фронтальной камеры',
        'video_back': 'Видео с основной камеры', 'photo': 'Фотография',
    },
    'plan_type': {
        'free': 'Бесплатный', 'premium_monthly': 'Premium — месяц',
        'premium_yearly': 'Premium — год', 'family_monthly': 'Семейный — месяц',
        'family_yearly': 'Семейный — год', 'corporate': 'Корпоративный',
    },
    'payment_provider': {'appstore': 'App Store', 'playstore': 'Google Play', 'admin': 'Администратор'},
    'relationship': {'parent': 'Родитель', 'child': 'Ребёнок', 'spouse': 'Супруг или супруга', 'friend': 'Друг', 'relative': 'Родственник'},
}


class QorgoAdminSite(AdminSite):
    """Custom admin site for Qorgo."""
    site_title = 'Админ-панель QORGO'
    site_header = 'QORGO — управление сервисом'
    index_title = 'Главная панель'
    enable_nav_sidebar = True

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        for app in app_list:
            app['name'] = APP_NAMES.get(app['app_label'], app['name'])
            for model in app['models']:
                key = f"{app['app_label']}.{model['object_name'].lower()}"
                model['name'] = MODEL_NAMES.get(key, model['name'])
        return app_list


class QorgoAdminLabelsMixin:
    """Translate standard field labels in administration forms."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if field and db_field.name in FIELD_LABELS:
            field.label = FIELD_LABELS[db_field.name]
        choice_labels = FIELD_CHOICES.get(db_field.name)
        if field and choice_labels and hasattr(field, 'choices'):
            field.choices = [
                (value, choice_labels.get(str(value), label))
                for value, label in field.choices
            ]
        return field

    def get_list_display(self, request):
        display = []
        for item in super().get_list_display(request):
            if not isinstance(item, str) or item not in FIELD_LABELS:
                display.append(item)
                continue

            method_name = f'_qorgo_label_{item}'
            if not hasattr(self.__class__, method_name):
                def column(admin_instance, obj, field_name=item):
                    return getattr(obj, field_name)

                column.__name__ = method_name
                column = admin.display(description=FIELD_LABELS[item], ordering=item)(column)
                setattr(self.__class__, method_name, column)
            display.append(method_name)
        return display


# Replace default admin site
admin.site.__class__ = QorgoAdminSite
