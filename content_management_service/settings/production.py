from content_management_service.settings.base import *

DEBUG = get_environment_var('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = get_environment_var('ALLOWED_HOSTS', '*').split(',')

SERVICE_DOMAIN = get_environment_var(
    'SERVICE_DOMAIN', 'https://cms.sepid.org/')

DB_NAME = get_environment_var('DB_NAME', 'workshop')
DB_USER = get_environment_var('DB_USER', 'user')
DB_PASS = get_environment_var('DB_PASS', 'p4s$pAsS')
DB_HOST = get_environment_var('DB_HOST', 'localhost')
DB_PORT = get_environment_var('DB_PORT', '5432')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

RD_HOST = get_environment_var("RD_HOST", 'redis://0.0.0.0:6379')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': RD_HOST,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

LOG_LEVEL = get_environment_var('LOG_LEVEL', 'INFO')

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
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(BASE_DIR, 'logging/debug.log'),
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': LOG_LEVEL,
            'propagate': True
        },
        'django': {
            'handlers': ['file', 'console'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'content_management_service': {
            'handlers': ['file', 'console'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
    },
}

SWAGGER_URL = f'{SERVICE_DOMAIN}api/'

CSRF_TRUSTED_ORIGINS = get_environment_var(
    'CSRF_TRUSTED_ORIGINS', '*').split(',')


########## FILE STORAGE ##########

STORAGES = {
    "default": {
        "BACKEND": "content_management_service.utils.storages.PublicS3Storage",
    },
    "staticfiles": {
        "BACKEND": "minio_storage.storage.MinioStaticStorage",
    },
}

###### S3 ######

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = get_environment_var('S3_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = get_environment_var('S3_SECRET_KEY')
AWS_STORAGE_BUCKET_NAME = get_environment_var('S3_BUCKET_NAME')
AWS_S3_REGION_NAME = get_environment_var('S3_REGION_NAME')
AWS_S3_ENDPOINT_URL = get_environment_var('S3_ENDPOINT_URL')
AWS_S3_USE_SSL = False
AWS_S3_VERIFY = True
AWS_DEFAULT_ACL = 'private'

# Fix for MissingContentLength: Force Content-Length header
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

###### MINIO ######

MINIO_STORAGE_ENDPOINT = get_environment_var('MINIO_STORAGE_ENDPOINT', None)
MINIO_STORAGE_ACCESS_KEY = get_environment_var(
    'MINIO_STORAGE_ACCESS_KEY', None)
MINIO_STORAGE_SECRET_KEY = get_environment_var(
    'MINIO_STORAGE_SECRET_KEY', None)
MINIO_STORAGE_USE_HTTPS = True
MINIO_STORAGE_MEDIA_BUCKET_NAME = 'media'
MINIO_STORAGE_STATIC_BUCKET_NAME = 'static'
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True
MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = True


########## Zarinpal Payment ##########

SANDBOX = False
ZARINPAL_MERCHANT_ID = get_environment_var('ZARINPAL_MERCHANT_ID', None)
