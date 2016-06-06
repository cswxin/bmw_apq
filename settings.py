# Django settings for mcreport project.

from releaseinfo import *
import os

DEBUG = REL_DEBUG
TEMPLATE_DEBUG = DEBUG

SITE_ROOT = REL_SITE_ROOT

RESOURCES_ROOT = os.path.join(SITE_ROOT, 'resources')

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

CACHE_BACKEND = REL_CACHE_BACKEND
CACHE_TIME = REL_CACHE_TIME

INTERNAL_IPS = ('127.0.0.1',)

DATABASES = {
    'default': {
        'ENGINE': DATABASE_ENGINE, # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DATABASE_NAME, # Or path to database file if using sqlite3.
        'USER': DATABASE_USER, # Not used with sqlite3.
        'PASSWORD': DATABASE_PASSWORD, # Not used with sqlite3.
        'HOST': DATABASE_HOST, # Set to empty string for localhost. Not used with sqlite3.
        'PORT': DATABASE_PORT, # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = REL_MEDIA_ROOT

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = REL_MEDIA_URL

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'


LOGIN_URL = '/'
LOGOUT_URL = '/logout/'
DATE_FORMAT = "Y-m-d"
# Make this unique, and don't share it with anybody.
SECRET_KEY = 'v&5%55*+hl!0ltatea2voxyr0!ik%(&5x)@=8i^z1e1yk=0$-c'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'userpro.ipmiddleware.IPMiddleware',
    #'djangodblog.DBLogMiddleware',
)

ROOT_URLCONF = 'bmw_apq.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITE_ROOT, 'mcview/templates'),
    os.path.join(SITE_ROOT, 'userpro/templates'),
    os.path.join(SITE_ROOT, 'mc/templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    
    'djangodblog',
    #'south',
    'survey',
    'mc',
    'userpro',
    'mcview',
    'policy'
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

#60 * 60 * 24
SESSION_COOKIE_AGE = 86400
#SESSION_EXPIRE_AT_BROWSER_CLOSE = True

DATETIME_FORMAT = "Y.m.d H:i:s"

MEDIA_STATIC_PATH = os.path.join(SITE_ROOT, 'static')

EMAIL_HOST = 'smtp.sohu.com'
EMAIL_HOST_USER = 'isurveylink'
EMAIL_HOST_PASSWORD = 'iloveidiaoyan'
DATA_VERSION = 1000
