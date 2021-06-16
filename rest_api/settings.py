"""
Django settings for rest_api project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'acgxmke(^6zrw6ke8olhdw1qo4ir8rp!5^a4uszk86j=cs$dcb'

# SECURITY WARNING: don't run with debug turned on in production!
ENVIRONMENT = os.environ.get("ENVIRONMENT", None)
PRODUCTION = ENVIRONMENT is not None and ENVIRONMENT.lower() == 'production'
DEBUG = not PRODUCTION

CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_METHODS = [
    'GET',
    'OPTIONS',
]

if PRODUCTION:
    print("REST API running in production environment.")
    EXTERNAL_IP = os.environ.get("EXTERNAL_IP", None)

    if not EXTERNAL_IP:
        print("No EXTERNAL_IP ENV detected!")
        quit()

    ALLOWED_HOSTS = ['{}'.format(EXTERNAL_IP)]
    CORS_ORIGIN_WHITELIST = (
        'http://{}'.format(EXTERNAL_IP),
    )
else:
    print("REST API running in development environment.")
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    CORS_ORIGIN_WHITELIST = (
        'http://localhost:4200',
    )

# Application definition

INSTALLED_APPS = [
    'rest_api',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mobility_5g_rest_api.apps.Mobility5GRestApiConfig',
    'rest_framework',
    'rest_framework_swagger',
    'drf_yasg',
    'corsheaders',
    'django_crontab'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rest_api.urls'

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

WSGI_APPLICATION = 'rest_api.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': os.environ.get('DB_NAME', '5g-mobility'),
        'CLIENT': {
            'host': os.environ.get('DB_HOST', 'localhost'),
            'port': int(os.environ.get('DB_PORT', 27017)),
            'username': os.environ.get('DB_USER', 'admin'),
            'password': os.environ.get('DB_PASSWORD', 'admin'),
            'authSource': os.environ.get('DB_AUTH', 'admin')
        },
        'TEST': {
            'NAME': 'test_' + os.environ.get('DB_NAME', '5g-mobility'),
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

# REST

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',

    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        # 'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
}

# Swagger

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': None,
    'SUPPORTED_SUBMIT_METHODS': [
        'get'
    ],
}

# Celery

CELERY_BROKER_URL = 'amqp://django:djangopass@' + \
                    os.environ.get('RABBIT_HOST', 'localhost') + ':5672/celery'
CELERY_RESULT_BACKEND = 'redis://:djangopass@' + \
                        os.environ.get('REDIS_HOST', 'localhost') + ':6379/0'

CELERY_TASK_TIME_LIMIT = 10 * 60
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Cronjobs
CRONJOBS = [
    ('00 18 * * *', 'mobility_5g_rest_api.cron.turn_off_cameras'),
    ('30 06 * * *', 'mobility_5g_rest_api.cron.turn_on_cameras')
]
