from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib import databrowse

from nominati.models import *
from nominati.views import EnteDetailView, EnteListView, EnteJSONListView, RegioneListView, RegioneDetailView, NazioneView, MergePersona_OP, RemovePersona_OP, NominatiHome, PartecipazioneJSONListView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', NominatiHome.as_view(), name="nominati_home"),
    url(r'^regioni/$', RegioneListView.as_view(), name="nominati_regione_list"),
    url(r'^regioni/(?P<pk>\d+)$', RegioneDetailView.as_view(), name="nominati_regione_detail"),
    url(r'^regioni/(?P<pk>\d+)?tipo=(?P<tipo>\w+)$', RegioneDetailView.as_view(), name="nominati_regione_tipologie"),
    url(r'^nazione/$', NazioneView.as_view(), name="nominati_nazione"),
    url(r'^nazione/?tipo=(?P<tipo>\w+)$', NazioneView.as_view(), name="nominati_nazione_tipologie"),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page' : '/'}, name='nominati_logout'),
    url(r'^enti/$', EnteListView.as_view(), name="nominati_ente_list"),
    # url(r'^enti.json$', EnteJSONListView.as_view(), name="nominati_ente_listJSON"),
    url(r'^enti/(?P<pk>\d+)$', EnteDetailView.as_view(), name="nominati_ente_detail"),
    # url(r'^partecipazioni.json$', PartecipazioneJSONListView.as_view(), name="nominati_partecipazione_listJSON"),
    url(r'^persona/merge_persona/$', MergePersona_OP.as_view(), name="merge_persona_op"),
    url(r'^persona/remove_persona/$', RemovePersona_OP.as_view(), name="remove_persona_op"),
    url(r'^databrowse/(.*)', databrowse.site.root),
    url(r'^utils/check_similars/(?P<object_id>\d+)', 'nominati.views.check_similars_views'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/',include('api.urls'))

)
