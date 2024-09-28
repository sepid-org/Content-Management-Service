import sys
from datetime import timedelta

from manage_content_service.settings.base import *

SECRET_KEY = get_environment_var(
    'SECRET_KEY', '*z!3aidedw32xh&1ew(^&5dgd17(ynnmk=s*mo=v2l_(4t_ff(')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SERVICE_DOMAIN = 'http://localhost:8000/'

ALLOWED_HOSTS = ['*']



# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)-8s [%(module)s:%(funcName)s:%(lineno)d]: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'manage_content_service': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

TESTING = sys.argv[1] == 'test'
# TESTING = True
STATIC_ROOT = get_environment_var('STATIC_ROOT', 'staticfiles')

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('JWT',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

ZARINPAL_CONFIG = {
    'ROUTE_START_PAY': 'https://sandbox.zarinpal.com/pg/StartPay/',
    'ROUTE_WEB_GATE': 'https://sandbox.zarinpal.com/pg/services/WebGate/wsdl',
    'MERCHANT': 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',  # Required
    'DESCRIPTION': 'ثبت‌نام در رویداد «رستاخیز: مسافر صفر» به صورت آزمایشی'  # Required
}
SWAGGER_URL = f'{SERVICE_DOMAIN}api/'


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


CSRF_TRUSTED_ORIGINS = [SERVICE_DOMAIN]
