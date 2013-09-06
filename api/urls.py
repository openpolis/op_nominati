from django.conf.urls import patterns, url, include
from rest_framework import routers
from api.views import EntiList, PartecipazioniList, ComposizionePartecipataList

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns('api.views',
    url(r'^$', 'api_root'),
    url(r'^enti/$', EntiList.as_view(),name='api-enti'),
    url(r'^partecipazioni/$', PartecipazioniList.as_view(),name='api-partecipazioni'),
    url(r'^composizione-partecipata/$', ComposizionePartecipataList.as_view(),name='api-composizione-partecipata'),
)