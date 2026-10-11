"""
Django settings for Qorgo project.
Generated using Django 5.1.
"""
import os
from pathlib import Path
from datetime import timedelta
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DJANGO_SECRET_KEY', default='dev-secret-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DJANGO_DEBUG', default=not bool(os.getenv('VERCEL')), cast=bool)

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='localhost,127.0.0.1,10.0.2.2,api.qorgo.services,qorgo-project-backend.vercel.app').split(',')
for variable in ('VERCEL_URL', 'VERCEL_PROJECT_PRODUCTION_URL'):
    if os.getenv(variable):
        ALLOWED_HOSTS.append(os.environ[variable])
CSRF_TRUSTED_ORIGINS = config('DJANGO_CSRF_TRUSTED_ORIGINS', default='https://api.qorgo.services,https://qorgo-project-backend.vercel.app').split(',')
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# Application definition
INSTALLED_APPS = [
    'daphne',  # Must be before django.contrib.staticfiles
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework.authtoken',
    'safety',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'phonenumber_field',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'channels',

    # Qorgo apps
    'content',
    'accounts',
    'families',
    'sos',
    'location',
    'geofences',
    'safety_timers',
    'notifications',
    'subscriptions',
    'analytics',
    'common',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'qorgo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'qorgo.wsgi.application'
ASGI_APPLICATION = 'qorgo.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=str(BASE_DIR / 'unified.sqlite3')),
        'USER': config('DB_USER', default='qorgo'),
        'PASSWORD': config('DB_PASSWORD', default='qorgo'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

DATABASE_URL = config('DATABASE_URL', default=config('POSTGRES_URL', default=''))
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.parse(DATABASE_URL, conn_max_age=0, conn_health_checks=True)
    if not DEBUG and DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
        DATABASES['default'].setdefault('OPTIONS', {}).setdefault('sslmode', 'require')
if os.getenv('VERCEL') and not DATABASE_URL:
    raise RuntimeError('Set DATABASE_URL to a PostgreSQL database before deploying on Vercel.')

if DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATABASES['default']['NAME'],
        'OPTIONS': {'timeout': 20},
    }

if not DEBUG and SECRET_KEY == 'dev-secret-key-change-in-production':
    raise RuntimeError('Set DJANGO_SECRET_KEY before using production settings.')

# Channel layers (Redis for WebSockets)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(config('REDIS_HOST', default='localhost'), config('REDIS_PORT', default=6379, cast=int))],
        },
    },
}

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Bishkek'
CELERY_BEAT_SCHEDULE = {
    'check-expired-safety-timers': {
        'task': 'qorgo.tasks.check_expired_safety_timers',
        'schedule': timedelta(minutes=1),
    },
    'mark-stale-locations': {
        'task': 'qorgo.tasks.mark_stale_locations',
        'schedule': timedelta(minutes=2),
    },
    'cleanup-old-location-history': {
        'task': 'qorgo.tasks.cleanup_old_location_history',
        'schedule': timedelta(hours=24),
    },
    'cleanup-expired-evidence': {
        'task': 'qorgo.tasks.cleanup_expired_evidence',
        'schedule': timedelta(hours=24),
    },
    'expire-subscriptions': {
        'task': 'qorgo.tasks.expire_subscriptions',
        'schedule': timedelta(hours=1),
    },
    'generate-daily-report': {
        'task': 'qorgo.tasks.generate_daily_report',
        'schedule': timedelta(hours=24),
    },
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'common.pagination.StandardPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'sos': '5/minute',  # SOS rate limiting
        'location_update': '60/minute',
    },
    'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# CORS
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://localhost:8000'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# Internationalization
LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Asia/Bishkek'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Firebase Admin SDK
FIREBASE_CREDENTIALS_PATH = config('FIREBASE_CREDENTIALS_PATH', default=None)
FIREBASE_DATABASE_URL = config('FIREBASE_DATABASE_URL', default=None)

# SMS Provider (for SOS alerts via SMS)
SMS_PROVIDER = config('SMS_PROVIDER', default='console')  # 'console', 'twilio', 'vonage'
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default=None)
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default=None)
TWILIO_FROM_NUMBER = config('TWILIO_FROM_NUMBER', default=None)
VONAGE_API_KEY = config('VONAGE_API_KEY', default=None)
VONAGE_API_SECRET = config('VONAGE_API_SECRET', default=None)

# Qorgo-specific settings
QORGO_EMERGENCY_NUMBERS = {
    'general': '112',
    'police': '102',
    'ambulance': '103',
    'fire': '101',
}
QORGO_FREE_MAX_FAMILY_MEMBERS = 5
QORGO_FREE_HISTORY_DAYS = 7
QORGO_PREMIUM_HISTORY_DAYS = 365
QORGO_LOCATION_ACTIVE_INTERVAL = 5  # seconds
QORGO_LOCATION_BACKGROUND_INTERVAL = 30  # seconds
QORGO_LOCATION_STALE_THRESHOLD = 120  # seconds

# drf-spectacular API docs
SPECTACULAR_SETTINGS = {
    'TITLE': 'Qorgo API',
    'DESCRIPTION': 'Personal and Family Safety App API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'ENUM_NAME_OVERRIDES': {
        'SOSStatusEnum': 'common.schema_choices.SOS_STATUS_CHOICES',
        'SafetyTimerStatusEnum': 'common.schema_choices.SAFETY_TIMER_STATUS_CHOICES',
        'SubscriptionStatusEnum': 'common.schema_choices.SUBSCRIPTION_STATUS_CHOICES',
        'ResolveAlertStatusEnum': ['resolved', 'false_alarm'],
        'UserRoleEnum': [('user', 'User'), ('admin', 'Admin'), ('emergency_operator', 'Emergency Operator')],
        'UserRoleUpdateEnum': ['user', 'admin', 'emergency_operator'],
        'FamilyRoleEnum': 'common.schema_choices.FAMILY_ROLE_CHOICES',
    },
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    'SWAGGER_UI_SETTINGS': {'deepLinking': True, 'persistAuthorization': False},
}

# Email login keeps the existing Flutter API compatible with the shared user model.
AUTHENTICATION_BACKENDS = ['accounts.backends.UsernameBackend', 'accounts.backends.EmailBackend', 'django.contrib.auth.backends.ModelBackend']
TWILIO_FROM = config('TWILIO_FROM', default=TWILIO_FROM_NUMBER or '')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('SMTP_HOST', default='')
EMAIL_PORT = config('SMTP_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('SMTP_USER', default='')
EMAIL_HOST_PASSWORD = config('SMTP_PASSWORD', default='')
EMAIL_USE_TLS = config('SMTP_TLS', default=True, cast=bool)
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = config('SMTP_FROM', default='')

JAZZMIN_SETTINGS = {
    'site_title': 'QORGO Admin',
    'site_header': 'QORGO',
    'site_brand': 'QORGO',
    'welcome_sign': 'Панель управления QORGO',
    'copyright': 'QORGO by DEO-CORE',
    'search_model': ['accounts.User'],
    'show_sidebar': True,
    'navigation_expanded': True,
    'topmenu_links': [
        {'name': 'Главная', 'url': 'admin:index', 'permissions': ['accounts.view_user']},
        {'name': 'Swagger API', 'url': 'swagger-ui', 'new_window': True},
        {'name': 'ReDoc', 'url': 'redoc', 'new_window': True},
    ],
    'icons': {
        'accounts.User': 'fas fa-user',
        'families.Family': 'fas fa-users',
        'sos.Alert': 'fas fa-exclamation-triangle',
        'location.ActiveLocation': 'fas fa-map-marker-alt',
        'geofences.Geofence': 'fas fa-map',
        'safety_timers.SafetyTimer': 'fas fa-clock',
        'subscriptions.Subscription': 'fas fa-credit-card',
    },
}
JAZZMIN_UI_TWEAKS = {'theme': 'flatly'}
