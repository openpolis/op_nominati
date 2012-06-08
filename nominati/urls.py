from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib import databrowse
from django.views.generic.simple import redirect_to

from nominati.models import *

admin.autodiscover()
databrowse.site.register(Comparto, Regione, Ente, Partecipata, Persona, Incarico)

urlpatterns = patterns('',
    url(r'^$', redirect_to, {'url': '/databrowse/'}),
    url(r'^databrowse/(.*)', databrowse.site.root),
    url(r'^utils/check_similars/(?P<object_id>\d+)', 'nominati.views.check_similars_views'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
