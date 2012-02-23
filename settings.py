#-*- coding: utf-8 -*-

import os

# Django settings for project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.split(__file__)[0], 'slono_job.sqlite3'),
        'OPTIONS': {"timeout": 30}
    }
}


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Omsk'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.split(__file__)[0], 'static')


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'el3m$fjdf69$2aca6+)%-+6w0837_(mk8$v)&op@a4z3*wxi2i'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'slono_job.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',

    'slono_job'
)


TWITTER_CONSUMER_KEY = "6zq0pgRkQuY5P0XpH8ncrA"
TWITTER_CONSUMER_SECRET = "dBXIavXbI8cWjU7vZHcuxTHDQ25Q38PESOJg8UqIQ"
TWITTER_ACCESS_KEY = "499288053-pihJLfSdUakvHQdv7KuSFZAUulb6Koqzi5f7Sp0M"
TWITTER_ACCESS_SECRET = "XSIdVGJVmkh36QrcamsZG0mQeU7h0NVdMYxToYVkM"

TWITTER_OWN_NAME = "SlonoJob"

TWITTER_TRIGGER_KEYWORDS = ["elephant", "elefant"]

TWITTER_INITIAL_QUOTES = [
    u"What is the difference between en elephant and a plum?",
    u"What does Tarzan say when he sees a herd of elephants in the distance?",
    u"How do you get four elephants into a Mini?",
    u"What game do four elephants in a mini play?",
    u"How do you get an elephant into the fridge?",
    u"How do you know there are two elephants in your fridge?",
]

TWITTER_TEMPLATE_REPLY = u"Don't say '%(original)s', just buy the elephant!!!"