# -*- coding: utf-8 -*-
## -*- mode: python -*-
## Django settings specific for your development environment should be placed below

from nominati.settings import *
from django.contrib.sites.models import Site



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(REPO_ROOT, 'sqlite.db'),
        }
}

ADMINS = (
    ('Administrator Name', 'admin@email.xx'),
    )
MANAGERS = ADMINS

# Root URLconf module for development installations
ROOT_URLCONF = 'nominati.urls_local'


# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
# ADMIN_MEDIA_PREFIX = '/static/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'xxxxx---'

# temporary
# INSTALLED_APPS = INSTALLED_APPS + ('django.contrib.databrowse',)

# ``django-debug-toolbar`` config
#MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware',)
#INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)

INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
    )

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    }

EMAIL_PORT = 25

OP_API_BASE_URL = 'http://api.openpolis.it/op/1.0'
OP_API_SIMILARITY_BASE_URL = '%s/similar_politicians' % OP_API_BASE_URL
OP_API_USER = 'xxxx'
OP_API_PASS = 'yyyy'

SITE_URL = "http://%s" % Site.objects.get(pk=SITE_ID).domain
OP_URL = 'http://politici.openpolis.it'

