from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib import databrowse

from nominati.models import *
from nominati.views import EnteDetailView, EnteListView, EnteJSONListView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', EnteListView.as_view(), name="nominati_ente_list"),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page' : '/'}, name='nominati_logout'),
    url(r'^enti.json$', EnteJSONListView.as_view(), name="nominati_ente_listJSON"),
    url(r'^enti/(?P<pk>\d+)$', EnteDetailView.as_view(), name="nominati_ente_detail"),
    url(r'^databrowse/(.*)', databrowse.site.root),
    url(r'^utils/check_similars/(?P<object_id>\d+)', 'nominati.views.check_similars_views'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

)
