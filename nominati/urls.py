from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib import databrowse
from nominati.models import *

admin.autodiscover()
databrowse.site.register(Comparto, Regione, Ente, Partecipata, Persona, Incarico)

urlpatterns = patterns('',
    url(r'^(.*)', databrowse.site.root),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
