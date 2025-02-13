from datetime import timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_environment_var(var_name, default, prefixed=True):
    if prefixed:
        var_name = 'CONTENT_MANAGEMENT_SERVICE_%s' % var_name
    return os.getenv(var_name, default)


SECRET_KEY = get_environment_var(
    'SECRET_KEY', '*z!3aidedw32xh&1ew(^&5dgd17(ynnmk=s*mo=v2l_(4t_ff(')


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/


# Application definition

DEFAULT_APPS = [
    'corsheaders',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

CUSTOM_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'import_export',
    'drf_yasg',
    'celery',
    'polymorphic',
    'django_extensions',
    'django_filters',
    'minio_storage',
    'shortener',
    'content_management_service.apps.MyAdminConfig',
    'apps.accounts.apps.AccountConfig',
    'apps.fsm.apps.FsmConfig',
    'apps.roadmap.apps.RoadmapConfig',
    'apps.contact.apps.ContactConfig',
    'apps.report.apps.ReportConfig',
    'apps.sale.apps.SaleConfig',
    'apps.file_storage.apps.FileStorageConfig',
    'apps.attributes.apps.AttributesConfig',
    'apps.response.apps.ResponseConfig',
    'apps.widgets.apps.WidgetsConfig',
    'apps.treasury.apps.TreasuryConfig',
]

INSTALLED_APPS = DEFAULT_APPS + CUSTOM_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # برای مدیریت CORS
    'django.middleware.security.SecurityMiddleware',  # برای امنیت
    'django.contrib.sessions.middleware.SessionMiddleware',  # برای مدیریت session
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # برای محافظت در برابر CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # برای احراز هویت
    'django.contrib.messages.middleware.MessageMiddleware',  # برای مدیریت پیام‌ها
    # برای محافظت در برابر clickjacking
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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


WSGI_APPLICATION = 'content_management_service.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/api/static/'

MEDIA_URL = '/api/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'sepid.platform@gmail.com'
EMAIL_HOST_PASSWORD = 'tmyz glmk cjsj urnw'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

CONSTANTS = {
    "PAGINATION_NUMBER": 50,
}

# Custom user model
AUTH_USER_MODEL = "accounts.User"

ASGI_APPLICATION = 'content_management_service.routing.application'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # احراز هویت JWT
        'rest_framework.authentication.SessionAuthentication',  # احراز هویت session
        # احراز هویت JWT از طریق کوکی‌ها:
        'content_management_service.authentication.cookie_jwt_authentication.CookieJWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',  # فیلترها
        'rest_framework.filters.OrderingFilter',  # مرتب‌سازی
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',  # صفحه‌بندی
    'PAGE_SIZE': 18,  # تعداد آیتم‌ها در هر صفحه
}


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

GUARDIAN_RAISE_403 = True
ANONYMOUS_USER_NAME = None

SWAGGER_SETTINGS = {
    'LOGIN_URL': '/api/auth/accounts/login/',
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    },
    'DEFAULT_AUTO_SCHEMA_CLASS': 'content_management_service.settings.custom_setting_classes.CustomAutoSchema',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'none',
}

VOUCHER_CODE_LENGTH = 5

DISCOUNT_CODE_LENGTH = 10

PURCHASE_UNIQ_CODE_LENGTH = 10


########## CORS ##########

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_PREFLIGHT_MAX_AGE = 86400  # Cache preflight برای ۲۴ ساعت (۸۶۴۰۰ ثانیه)

CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "OPTIONS",
    "PATCH",
]

CORS_ALLOW_HEADERS = [
    "Accept",
    "Accept-Encoding",
    "Content-Type",
    "DNT",
    "Origin",
    "User-Agent",
    "X-CSRFToken",
    "X-Requested-With",
    "Website",  # هدر سفارشی
    "FSM",      # هدر سفارشی
]


########## CSRF ##########

COOKIE_DOMAIN = get_environment_var("COOKIE_DOMAIN", ".sepid.com")

# امنیت کوکی‌ها
SESSION_COOKIE_HTTPONLY = True  # جلوگیری از دسترسی JavaScript به کوکی‌ها
SESSION_COOKIE_SAMESITE = 'None'  # برای دامنه‌های مختلف
SESSION_COOKIE_SECURE = True  # فقط از طریق HTTPS ارسال شود
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'None'  # برای دامنه‌های مختلف
CSRF_COOKIE_SECURE = True  # فقط از طریق HTTPS ارسال شود


########## JWT ##########

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('JWT',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}


########## Celery ##########

CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
ROOT_URLCONF = 'content_management_service.urls'
CELERY_BROKER_URL = get_environment_var('BROKER_URL', 'amqp://')


########## METABASE ##########

METABASE_URL = get_environment_var('METABASE_URL', None)
METABASE_USERNAME = get_environment_var('METABASE_USERNAME', None)
METABASE_PASSWORD = get_environment_var('METABASE_PASSWORD', None)


########## OTHER SERVICES ##########

WMS_URL = get_environment_var('WMS_URL', 'http://localhost:10000/')

IMS_URL = get_environment_var(
    'IMS_URL', 'https://ims.sepid.org/')

BANK_URL = get_environment_var('BANK_URL', '"https://bank.sepid.org"')

ASSESS_ANSWER_SERVICE_URL = get_environment_var(
    'ASSESS_ANSWER_SERVICE_URL', 'https://aas.sepid.org/')

SHAD_LOGIN_USERNAME = get_environment_var('SHAD_LOGIN_USERNAME', None)
SHAD_LOGIN_PASSWORD = get_environment_var('SHAD_LOGIN_PASSWORD', None)

KAVENEGAR_TOKEN = get_environment_var('KAVENEGAR_TOKEN', None)
