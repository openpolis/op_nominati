from django.conf.urls import patterns, url, include
from rest_framework import routers
from api.views import EntiList, PartecipazioniList

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns('',
    url(r'^enti/$', EntiList.as_view(),name='api_enti'),
    url(r'^partecipazioni/$', PartecipazioniList.as_view(),name='api_partecipazioni'),
)