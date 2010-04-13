# -*- coding: utf-8 -*-

# Django settings for tagfs project.

import os
import sys

# Add to the Python path the directory containing the packages in the source distribution. 
PACKAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, os.pardir))
sys.path.insert(0, PACKAGES_DIR)

# Add the contrib directory to the Python path.
CONTRIB_DIR = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, 'contrib')
sys.path.insert(0, os.path.abspath(CONTRIB_DIR))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Abel Puentes Luberta', 'abelchino@lab.matcom.uh.cu'),
    ('Andy Venet Pompa', 'vangelis@lab.matcom.uh.cu'), 
    ('Ariel Hernández Amador', 'gnuaha7@uh.cu'),
    ('Yasser González Fernández', 'yglez@uh.cu'),     
)

MANAGERS = ADMINS

# 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_ENGINE = 'sqlite3' 
# Or path to database file if using sqlite3.
DATABASE_NAME = os.path.join(os.path.dirname(__file__), os.pardir, 'data/debug.db')

# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Havana'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), os.pardir, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '^!z^!o$f=z3mv9r3t(dtn!4rk6notu$t#=7xx3)+k&x0il8+ce'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'tagfs.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), os.pardir, 'templates'),
)

if DEBUG:
    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',        
        'django.contrib.admin',
    )
else:
    INSTALLED_APPS = ()

INSTALLED_APPS += (
    'project.app',
)

#Client Instance
from tagfs.client import TagFSClient
ADDRESS = '127.0.0.1'
TAGFSCLIENT = TagFSClient(ADDRESS)