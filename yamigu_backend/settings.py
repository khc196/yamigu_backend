"""
Django settings for yamigu_backend project.

Generated by 'django-admin startproject' using Django 2.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import firebase_admin
from firebase_admin import credentials, db
import environ
from OpenSSL import crypto

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
environ.Env.read_env()
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'rest_framework.authtoken',
    'core',
    'authorization',
    'rest_auth',
    'django.contrib.sites',
    'drf_yasg',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.kakao',
    'allauth.socialaccount.providers.apple',
    'fcm_django',
    'sslserver',
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


ACCOUNT_AUTHENTICATION_METHOD = 'name'
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'name'
ACCOUNT_USERNAME_REQUIRED = False
AUTH_USER_MODEL = 'authorization.User'

SITE_ID=1

SOCIALACCOUNT_ADAPTER = 'authorization.adapter.SocialAccountAdapter'

REST_AUTH_SERIALIZERS = { 'USER_DETAILS_SERIALIZER':'authorization.serializers.UserSerializer' }

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_HTTPONLY = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_PAGINATION_CLASS':
        'core.utils.pagination.MyPageNumberPagination',

}

ROOT_URLCONF = 'yamigu_backend.urls'

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

WSGI_APPLICATION = 'yamigu_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        }
    },
    'OPERATION_SORTER': None,
}
cred = credentials.Certificate(os.path.join(BASE_DIR, 'credentials.json'))
try :
	default_app = firebase_admin.initialize_app(cred,  {'databaseURL': env('FIREBASE_DB_URL')})
except ValueError:
	pass

FCM_DJANGO_SETTINGS = {
        "APP_VERBOSE_NAME": "com.yamigu.yamigu_app",
         # default: _('FCM Django')
        "FCM_SERVER_KEY": env('FCM_SERVER_KEY'),
         # true if you want to have only one active device per registered user at a time
         # default: False
        "ONE_DEVICE_PER_USER": False,
         # devices to which notifications cannot be sent,
         # are deleted upon receiving error response from FCM
         # default: False
        "DELETE_INACTIVE_DEVICES": False,
}

MANAGER_ID = env('MANAGER_ID')

SOCIAL_AUTH_APPLE_KEY_ID = env('SOCIAL_AUTH_APPLE_KEY_ID')
privkey_file = open(env('SOCIAL_AUTH_APPLE_PRIVATE_KEY'), 'r')
#p12 = crypto.load_pkcs12(open(privkey_file, "rb").read(), env("APPLE_DEV_PW"))

SOCIAL_AUTH_APPLE_PRIVATE_KEY = privkey_file.read()
#print(SOCIAL_AUTH_APPLE_PRIVATE_KEY)
SOCIAL_AUTH_APPLE_TEAM_ID = env('SOCIAL_AUTH_APPLE_TEAM_ID')
SOCIAL_AUTH_APPLE_CLIENT_ID = env('SOCIAL_AUTH_APPLE_CLIENT_ID')

SOCIAL_AUTH_URL_NAMESPACE = 'social'
