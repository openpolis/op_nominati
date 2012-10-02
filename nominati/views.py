from django.db.models.aggregates import Count, Sum
from django.db.models.query_utils import Q
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.core.serializers import serialize
from django.conf import settings
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.db.models.query import QuerySet
from django.utils.functional import curry
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from nominati.models import Incarico, Ente, Persona, TipoCarica, Regione, Partecipata
import json
from json.encoder import JSONEncoder
import urllib2
from datetime import datetime, timedelta

class AccessControlView(object):
    """
    Define access control for the view
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AccessControlView, self).dispatch(*args, **kwargs)


class DjangoJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, QuerySet):
            # `default` must return a python serializable
            # structure, the easiest way is to load the JSON
            # string produced by `serialize` and return it
            return json.loads(serialize('json', obj))
        return JSONEncoder.default(self,obj)
dumps = curry(json.dumps, cls=DjangoJSONEncoder)

class JSONResponseMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return HttpResponse(content,
                            content_type='application/json',
                            **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return dumps(context)


class EnteListView(AccessControlView, ListView):
    model = Ente

    def get_context_data(self, **kwargs):
        context = super(EnteListView, self).get_context_data(**kwargs)
        context['SITE_URL'] = settings.SITE_URL
        return context

    def get_queryset(self):
        if 'qterm' in self.request.GET:
            qterm = self.request.GET['qterm']
            return Ente.objects.filter(denominazione__icontains=qterm)[0:50]
        else:
            return Ente.objects.all()[0:50]


class RegioneListView(AccessControlView, ListView):
    model = Regione



class RegioneDetailView(AccessControlView, DetailView):
    model = Regione
    context_object_name = "regione"

    def get_context_data(self, **kwargs ):
        context = super(RegioneDetailView, self).get_context_data(**kwargs)
        r = self.get_object()
        tipologia = self.request.GET.get('tipo',)

        context['SITE_URL'] = settings.SITE_URL
        context['OP_URL'] = settings.OP_URL

        now = datetime.now()
        context['table'] = []
        context['base_template']='nominati/regione_detail.html'
        partecipate = Partecipata.objects.filter(ente__regione = r).distinct()
        context['n_partecipate'] = Partecipata.objects.filter(ente__regione = r).distinct().count()
        if tipologia != '':
            if tipologia =='part_tipologia':
                context['table'] = partecipate.order_by('tipologia_partecipata')
                self.template_name = "nominati/part_tipologia.html"
            if tipologia == 'part_competenze':
                context['table'] = partecipate.order_by('-competenza_partecipata')
                self.template_name = "nominati/part_competenze.html"
            if tipologia == 'part_finalita':
                context['table'] = partecipate.order_by('-finalita_partecipata')
                self.template_name = "nominati/part_finalita.html"
            if tipologia == 'part_resoconto':
                context['table'] = partecipate.order_by('bilancio__resoconto').distinct()
                self.template_name = "nominati/part_resoconto.html"
            if tipologia == 'amm_tot':
                incarichi = Incarico.objects.filter(ente_nominante_cf__regione = r).\
                filter(Q(data_inizio__lte=now) &
                       (Q(data_fine__gte=now) | Q(data_fine__isnull=True)))
                context['n_amministratori'] = incarichi.values('persona').distinct().count()
                context['n_amministratori_uomini'] = incarichi.filter(persona__sesso=1).values('persona').distinct().count()
                context['n_amministratori_donne'] = incarichi.filter(persona__sesso=0).values('persona').distinct().count()

                # age levels and filters
                ages = [
                            {
                                'age':'under 25',
                                'filters': {
                                    'persona__data_nascita__gt': now-timedelta(days=9131.05),
                                    }
                            },
                            {
                                'age':'tra 25 e 35',
                                'filters': {
                                    'persona__data_nascita__gt': now-timedelta(days=12783.5),
                                    'persona__data_nascita__lte': now-timedelta(days=9131.05),
                                    }
                            },
                            {
                                'age':'tra 35 e 45',
                                'filters': {
                                    'persona__data_nascita__gt': now-timedelta(days=16435.9),
                                    'persona__data_nascita__lte': now-timedelta(days=12783.5),
                                    }
                            },
                            {
                                'age':'tra 45 e 55',
                                'filters': {
                                    'persona__data_nascita__gt': now-timedelta(days=20088.3),
                                    'persona__data_nascita__lte': now-timedelta(days=16435.9),
                                    }
                            },
                            {
                                'age':'tra 55 e 65',
                                'filters': {
                                    'persona__data_nascita__gt': now-timedelta(days=23740.7),
                                    'persona__data_nascita__lte': now-timedelta(days=20088.3),
                                    }
                            },
                            {
                                'age':'over 65',
                                'filters': {
                                    'persona__data_nascita__lte': now-timedelta(days=23740.7),
                                    }
                            },
                            {
                                'age':'unknown',
                                'filters': {
                                    'persona__data_nascita__isnull': True,
                                    }
                            },
                    ]


                for item in ages:
                    context['table'].append({
                        'age': item['age'],
                        'all': incarichi.filter(**item['filters']).values('persona').distinct().count(),
                        'male': incarichi.\
                            filter(**item['filters']).filter(persona__sesso=Persona.MALE_SEX).\
                            values('persona').distinct().count(),
                        'female': incarichi.\
                            filter(**item['filters']).filter(persona__sesso=Persona.FEMALE_SEX).\
                            values('persona').distinct().count(),
                    })
                context['n_amministratori_tipo_carica'] = []
                for c in TipoCarica.objects.all():
                    context['n_amministratori_tipo_carica'].append(
                        {
                            'denominazione': c.denominazione,
                            'tot': incarichi.filter(tipo_carica=c).values('persona').distinct().count(),
                            'uomini': incarichi.filter(tipo_carica=c).\
                            filter(persona__sesso=Persona.MALE_SEX).\
                            values('persona').distinct().count(),
                            'donne': incarichi.filter(tipo_carica=c).\
                            filter(persona__sesso=Persona.FEMALE_SEX).\
                            values('persona').distinct().count()
                        }
                )

                self.template_name = 'nominati/amm_tot.html'

            if tipologia == 'amm_politici':
                incarichi = Incarico.objects.filter(ente_nominante_cf__regione = r).\
                    filter(Q(data_inizio__lte=now) &
                           (Q(data_fine__gte=now) | Q(data_fine__isnull=True)))
                context['table'] = incarichi.\
                    filter(persona__openpolis_id__isnull=False).exclude(persona__openpolis_id='').distinct()

                self.template_name = 'nominati/amm_politici.html'

            if tipologia == 'amm_incarichi':
                incarichi = Incarico.objects.filter(ente_nominante_cf__regione = r).\
                filter(Q(data_inizio__lte=now) &
                       (Q(data_fine__gte=now) | Q(data_fine__isnull=True)))
                context['table'] = incarichi.\
                    values('persona', 'persona__nome', 'persona__cognome').\
                    annotate(n=Count('persona')).order_by('-n')

                self.template_name = 'nominati/amm_incarichi.html'

            if tipologia == 'amm_compenso':
                incarichi = Incarico.objects.filter(ente_nominante_cf__regione = r).\
                filter(Q(data_inizio__lte=now) &
                       (Q(data_fine__gte=now) | Q(data_fine__isnull=True)))
                context['table'] = incarichi.\
                    values('persona', 'persona__nome', 'persona__cognome').\
                    annotate(s=Sum('compenso_totale')).order_by('-s')

                self.template_name = 'nominati/amm_compenso.html'

            if tipologia == 'lista_nominati':
                incarichi = Incarico.objects.filter(ente_nominante_cf__regione = r).\
                    filter(Q(data_inizio__lte=now) &
                           (Q(data_fine__gte=now) | Q(data_fine__isnull=True)))
                persone_id = incarichi.values('persona','persona__cognome').distinct().order_by('persona__cognome')

                context['table']=\
                [
                (
                    p['persona__cognome'],
                    {
                        'persona': Persona.objects.get(pk=p['persona']),
                        'incarichi':Incarico.objects.filter(persona = p['persona'], ente_nominante_cf__regione = r)
                    }
                    )
                for p in persone_id
                ]

                self.template_name = 'nominati/lista_nominati.html'

        return context

class NazioneView(AccessControlView, TemplateView):

    template_name = 'nominati/nazione_detail.html'

    def get_context_data(self, **kwargs):
        context = super(NazioneView, self).get_context_data(**kwargs)
        tipologia = self.request.GET.get('tipo',)

        context['SITE_URL'] = settings.SITE_URL
        context['OP_URL'] = settings.OP_URL

        now = datetime.now()
        context['table'] = []
        context['base_template']='nominati/nazione_detail.html'
        partecipate = Partecipata.objects.all().distinct()
        context['n_partecipate'] = partecipate.count()

        if tipologia != '':
            if tipologia =='part_tipologia':
                partecipate = Partecipata.objects.all().distinct().select_related('tipologia_partecipata')
                context['table'] = partecipate.order_by('tipologia_partecipata')
                self.template_name = "nominati/part_tipologia.html"
            if tipologia == 'part_competenze':
                partecipate = Partecipata.objects.all().distinct().select_related('competenza_partecipata')
                context['table'] = partecipate.order_by('competenza_partecipata')
                self.template_name = "nominati/part_competenze.html"
            if tipologia == 'part_resoconto':

                context['table'] = partecipate.order_by('bilancio__resoconto').distinct()
                self.template_name = "nominati/part_resoconto.html"
            if tipologia == 'amm_tot':
                incarichi = Incarico.objects.all().\
                filter(Q(data_inizio__lte=now) &
                       (Q(data_fine__gte=now) | Q(data_fine__isnull=True)))
                context['n_amministratori'] = incarichi.values('persona').distinct().count()
                context['n_amministratori_uomini'] = incarichi.filter(persona__sesso=1).values('persona').distinct().count()
                context['n_amministratori_donne'] = incarichi.filter(persona__sesso=0).values('persona').distinct().count()

                # age levels and filters
                ages = [
                    {
                        'age':'under 25',
                        'filters': {
                            'persona__data_nascita__gt': now-timedelta(days=9131.05),
                            }
                    },
                    {
                        'age':'tra 25 e 35',
                        'filters': {
                            'persona__data_nascita__gt': now-timedelta(days=12783.5),
                            'persona__data_nascita__lte': now-timedelta(days=9131.05),
                            }
                    },
                    {
                        'age':'tra 35 e 45',
                        'filters': {
                            'persona__data_nascita__gt': now-timedelta(days=16435.9),
                            'persona__data_nascita__lte': now-timedelta(days=12783.5),
                            }
                    },
                    {
                        'age':'tra 45 e 55',
                        'filters': {
                            'persona__data_nascita__gt': now-timedelta(days=20088.3),
                            'persona__data_nascita__lte': now-timedelta(days=16435.9),
                            }
                    },
                    {
                        'age':'tra 55 e 65',
                        'filters': {
                            'persona__data_nascita__gt': now-timedelta(days=23740.7),
                            'persona__data_nascita__lte': now-timedelta(days=20088.3),
                            }
                    },
                    {
                        'age':'over 65',
                        'filters': {
                            'persona__data_nascita__lte': now-timedelta(days=23740.7),
                            }
                    },
                    {
                        'age':'unknown',
                        'filters': {
                            'persona__data_nascita__isnull': True,
                            }
                    },
                    ]


                for item in ages:
                    context['table'].append({
                        'age': item['age'],
                        'all': incarichi.filter(**item['filters']).values('persona').distinct().count(),
                        'male': incarichi.\
                        filter(**item['filters']).filter(persona__sesso=Persona.MALE_SEX).\
                        values('persona').distinct().count(),
                        'female': incarichi.\
                        filter(**item['filters']).filter(persona__sesso=Persona.FEMALE_SEX).\
                        values('persona').distinct().count(),
                        })
                context['n_amministratori_tipo_carica'] = []
                for c in TipoCarica.objects.all():
                    context['n_amministratori_tipo_carica'].append(
                        {
                            'denominazione': c.denominazione,
                            'tot': incarichi.filter(tipo_carica=c).values('persona').distinct().count(),
                            'uomini': incarichi.filter(tipo_carica=c).\
                            filter(persona__sesso=Persona.MALE_SEX).\
                            values('persona').distinct().count(),
                            'donne': incarichi.filter(tipo_carica=c).\
                            filter(persona__sesso=Persona.FEMALE_SEX).\
                            values('persona').distinct().count()
                        }
                    )

                self.template_name = 'nominati/amm_tot.html'

            if tipologia == 'amm_politici':
                incarichi = Incarico.objects.all().\
                filter(Q(data_inizio__lte=now) &
                       (Q(data_fine__gte=now) | Q(data_fine__isnull=True)))
                context['table'] = incarichi.\
                filter(persona__openpolis_id__isnull=False).exclude(persona__openpolis_id='').distinct()

                self.template_name = 'nominati/amm_politici.html'

            if tipologia == 'amm_incarichi':
                incarichi = Incarico.objects.all().\
                filter(Q(data_inizio__lte=now) &
                       (Q(data_fine__gte=now) | Q(data_fine__isnull=True)))
                context['table'] = incarichi.\
                values('persona', 'persona__nome', 'persona__cognome').\
                annotate(n=Count('persona')).order_by('-n')

                self.template_name = 'nominati/amm_incarichi.html'

            if tipologia == 'amm_compenso':
                incarichi = Incarico.objects.all().\
                filter(Q(data_inizio__lte=now) &
                       (Q(data_fine__gte=now) | Q(data_fine__isnull=True)))
                context['table'] = incarichi.\
                values('persona', 'persona__nome', 'persona__cognome').\
                annotate(s=Sum('compenso_totale')).order_by('-s')

                self.template_name = 'nominati/amm_compenso.html'

            if tipologia == 'lista_nominati':
                incarichi = Incarico.objects.all().\
                filter(Q(data_inizio__lte=now) &
                       (Q(data_fine__gte=now) | Q(data_fine__isnull=True)))
                persone_id = incarichi.values('persona','persona__cognome').distinct().order_by('persona__cognome')

                context['table']=\
                [
                (
                    p['persona__cognome'],
                    {
                        'persona': Persona.objects.get(pk=p['persona']),
                        'incarichi':Incarico.objects.filter(persona = p['persona'],)
                    }
                    )
                for p in persone_id
                ]

                self.template_name = 'nominati/lista_nominati.html'


        return context


class EnteJSONListView(JSONResponseMixin, EnteListView):
    def convert_context_to_json(self, context):
        return dumps(context['ente_list'])


class EnteDetailView(AccessControlView, DetailView):
    model = Ente
    context_object_name = "ente"
    queryset = Ente.objects.all()

    def get_context_data(self, **kwargs):
        context = super(EnteDetailView, self).get_context_data(**kwargs)
        e = self.get_object()
        context['SITE_URL'] = settings.SITE_URL
        context['OP_URL'] = settings.OP_URL
        context['partecipate_by_tipologia'] = e.partecipata_set.all().order_by('tipologia_partecipata')
        context['partecipate_by_competenza'] = e.partecipata_set.all().order_by('competenza_partecipata')
        context['partecipate_by_resoconto'] = e.partecipata_set.all().order_by('bilancio__resoconto').distinct()
        now = datetime.now()
        incarichi = Incarico.objects.filter(ente_nominante_cf=e.codice_fiscale).\
                        filter(Q(data_inizio__lte=now) &
                               (Q(data_fine__gte=now) | Q(data_fine__isnull=True)))
        context['n_amministratori'] = incarichi.values('persona').distinct().count()
        context['n_amministratori_uomini'] = incarichi.filter(persona__sesso=1).values('persona').distinct().count()
        context['n_amministratori_donne'] = incarichi.filter(persona__sesso=0).values('persona').distinct().count()

        # age levels and filters
        ages = {
            'under_25': { 
                'filters': {
                    'persona__data_nascita__gt': now-timedelta(days=9131.05),
                }
            },
            'under_35': {
                'filters': {
                    'persona__data_nascita__lt': now-timedelta(days=12783.5),
                    'persona__data_nascita__gt': now-timedelta(days=9131.05),
                }
            },
            'under_45': {
                'filters': {
                    'persona__data_nascita__lt': now-timedelta(days=16435.9),
                    'persona__data_nascita__gt': now-timedelta(days=12783.5),
                }
            },
            'under_55': {
                'filters': {
                    'persona__data_nascita__gt': now-timedelta(days=20088.3),
                    'persona__data_nascita__lte': now-timedelta(days=16435.9),
                }
            },
            'under_65': {
                'filters': {
                    'persona__data_nascita__gt': now-timedelta(days=23740.7),
                    'persona__data_nascita__lte': now-timedelta(days=20088.3),
                }
            },
            'over_65': {
                'filters': {
                    'persona__data_nascita__lte': now-timedelta(days=23740.7),
                }
            },            
            'unknown': {
                'filters': {
                    'persona__data_nascita__isnull': True,
                }
            },
        }
        
        # dynamically build extractions for age levels
        for age, params in ages.items():            
            context['n_amministratori_%s' % age] = incarichi.filter(**params['filters']).\
                values('persona').distinct().count()
            context['n_amministratori_%s_uomini' % age] = incarichi.\
                filter(**params['filters']).filter(persona__sesso=Persona.MALE_SEX).\
                values('persona').distinct().count()
            context['n_amministratori_%s_donne' % age] = incarichi.\
                filter(**params['filters']).filter(persona__sesso=Persona.FEMALE_SEX).\
                values('persona').distinct().count()

        context['n_amministratori_tipo_carica'] = []
        for c in TipoCarica.objects.all():
            context['n_amministratori_tipo_carica'].append(
                {
                    'denominazione': c.denominazione, 
                    'tot': incarichi.filter(tipo_carica=c).values('persona').distinct().count(),
                    'uomini': incarichi.filter(tipo_carica=c).\
                        filter(persona__sesso=Persona.MALE_SEX).\
                        values('persona').distinct().count(),
                    'donne': incarichi.filter(tipo_carica=c).\
                        filter(persona__sesso=Persona.FEMALE_SEX).\
                        values('persona').distinct().count()
                }
            )

        context['amministratori_politici'] = incarichi.\
            filter(persona__openpolis_id__isnull=False).exclude(persona__openpolis_id='').distinct()

        context['amministratori_compensi'] = incarichi.\
                filter(ente_nominante_cf=e.codice_fiscale).\
                values('persona', 'persona__nome', 'persona__cognome').\
                annotate(s=Sum('compenso_totale')).order_by('-s')
        
        context['amministratori_incarichi'] = incarichi.\
            filter(ente_nominante_cf=e.codice_fiscale).\
            values('persona', 'persona__nome', 'persona__cognome').\
            annotate(n=Count('persona')).order_by('-n')

        persone_id = incarichi.values('persona','persona__cognome').distinct().order_by('persona__cognome')

        context['lista_nominati']=\
        [
        (
            p['persona__cognome'],
            {
                'persona': Persona.objects.get(pk=p['persona']),
                'incarichi':Incarico.objects.filter(persona = p['persona'], ente_nominante_cf=e.codice_fiscale)
            }
            )
        for p in persone_id
        ]

        return context


def home(self):
    return render_to_response('nominati/home.html')


def check_similars_views(request, object_id):
    if not (request.user.is_authenticated() and request.user.is_staff):
        return HttpResponseNotFound('<h1>Page not found</h1>')
        
    obj = Persona.objects.get(pk=object_id)
    
    url = "http://api.openpolis.it/op/1.0/similar_politicians/"
    url += "?first_name=%s&last_name=%s" % (obj.nome, obj.cognome)
    #, content_type='application/json; charset=utf-8'
    return HttpResponse(json.dumps(get_json_response(url), indent=4), mimetype="application/json")
    
    
def get_json_response(url):
    """
    generic method to get json response from url,
    using basic authentication
    """
    username = settings.OP_API_USER
    password = settings.OP_API_PASS

    # this creates a password manager
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, username, password)
    # because we have put None at the start it will always
    # use this username/password combination for  urls
    # for which `theurl` is a super-url

    authhandler = urllib2.HTTPBasicAuthHandler(passman)
    # create the AuthHandler

    opener = urllib2.build_opener(authhandler)
    urllib2.install_opener(opener)
    # All calls to urllib2.urlopen will now use our handler
    # Make sure not to include the protocol in with the URL, or
    # HTTPPasswordMgrWithDefaultRealm will be very confused.
    # You must (of course) use it when fetching the page though.

    response = urllib2.urlopen(url)
    return json.loads(response.read())    