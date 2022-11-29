import os
from datetime import timedelta

# JWT settings.
from aaa.settings_jwt import *
from aaa.settings_workflow import *

# Identity provider.
# from aaa.identityProvider.ldap_conf import *
from aaa.identityProvider.ad_conf import *
from aaa.identityProvider.radius_conf import *


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'o7lx@83-%tdncpo0qx4h#nbf-kd_bbswajgrvigy55-c8z!#dz'

# SECURITY WARNING: don't run with debug turned on in production!
# Setting this one to true log also all mysql queries.
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
# To include the app in our project add a reference to its configuration class in the INSTALLED_APPS.
# The AwxConfig class is in the sso/apps.py file, so its dotted path is 'sso.apps.AwxConfig'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'sso.middleware.Log.LogMiddleware',
    'sso.middleware.HTTP.HTTPMiddleware',
]

ROOT_URLCONF = 'aaa.urls'

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

WSGI_APPLICATION = 'aaa.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
# Do not remove comments below.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sso',
        'USER': 'sso', #DATABASE_USER
        'PASSWORD': 'password', #DATABASE_PASSWORD
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'django': {
            'format': 'DJANGO_SSO - %(message)s',
        },
        'http': {
            'format': 'HTTP_SSO - %(message)s',
        },
    },

    'handlers': {
        #'file': {
        #    'level': 'DEBUG',
        #    'class': 'logging.FileHandler',
        #    'filename': '/var/log/django-aaa/django-aaa.log',
        #},
        'syslog_django': {
            'class': 'logging.handlers.SysLogHandler',
            'level': 'DEBUG',
            'address': '/dev/log',
            'facility': 'local0',
            'formatter': 'django',
        },
        'syslog_http': {
            'class': 'logging.handlers.SysLogHandler',
            'level': 'DEBUG',
            'address': '/dev/log',
            'facility': 'local0',
            'formatter': 'http',
        },
    },

    'loggers': {
        'django': {
            'handlers': ['syslog_django'],
            'level': 'DEBUG',
            'propagate': False
        },
        'http': {
            'handlers': ['syslog_http'],
            'level': 'DEBUG',
            'propagate': False
        },
        '': {
            'handlers': ['syslog_django'],
            'level': 'DEBUG',
        },
    },
}

# Django REST Framework.

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'radiusauth.backends.RADIUSBackend',
    "django_auth_ldap.backend.LDAPBackend",
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTTokenUserAuthentication',
    ],

    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/minute',
        'user': '60/minute'
    },

    # Disable browser-view for APIs.
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=1440),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'RS256',
    'SIGNING_KEY': JWT_TOKEN['privateKey'],
    'VERIFYING_KEY': JWT_TOKEN['publicKey'],
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    #'USER_ID_FIELD': 'uid',
    #'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1)
}

SUPERADMIN_IDENTITY_AD_GROUPS = ["cn=groupGods,cn=users,dc=lab,dc=local"]
