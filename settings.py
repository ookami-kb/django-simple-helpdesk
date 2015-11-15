"""
Django settings for helpdesk project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(__file__)

try:
    from local_settings import *
except:
    from local_settings_default import *

SECRET_KEY = 'e&0(!y8&ni4phx045_k29obf%0zw#*_3_x953rgn8l)hmmuf6@'

ALLOWED_HOSTS = []

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'helpdesk',
    'widget_tweaks',
    'tastypie',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "node_modules"),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(pathname)s:%(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'helpdesk': {
            'filename': BASE_DIR + '/helpdesk.log',
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'formatter': 'simple',
        }
    },
    'loggers': {
        'helpdesk.mail': {
            'handlers': ['helpdesk'],
            'level': 'INFO',
        }
    },
}

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CKEDITOR_UPLOAD_PATH = MEDIA_ROOT + '/ckeditor/'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': [
            ['Source', '-', 'Bold', 'Italic', '-', 'NumberedList', 'BulletedList', '-', 'RemoveFormat'],
            ['Cut', 'Copy', 'Paste', 'PasteText', '-', 'Undo', 'Redo']
        ],
        'height': 300,
        'width': '100%',
    },
}

SITE_ID = 1
