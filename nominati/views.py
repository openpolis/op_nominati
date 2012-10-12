from django.db.models.aggregates import Count, Sum
from django.db.models.query_utils import Q
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, redirect
from django.core.serializers import serialize
from django.conf import settings
from django.views.generic import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.db.models.query import QuerySet
from django.utils.functional import curry
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from nominati.models import Incarico, Ente, Persona, TipoCarica, Regione, Partecipata, Bilancio
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


class PartecipateView(AccessControlView):
    model = None
    incarichi = []
    partecipate = []
    context_object_name=''
    base_template=''
    context = {}


    def get_context_data(self, **kwargs ):
        context = super(PartecipateView, self).get_context_data(**kwargs)

        tipologia = self.request.GET.get('tipo',)

        context['SITE_URL'] = settings.SITE_URL
        context['OP_URL'] = settings.OP_URL

        now = datetime.now()
        context['table'] = []
        context['base_template'] =  self.base_template
        self.template_name = self.base_template
        partecipate = self.partecipate
        incarichi = self.incarichi
        context['base_template']= self.base_template

        if tipologia != '':

            if tipologia =='part_tipologia':
                context['table'] = partecipate.\
                    annotate(n_inc=Count('incarico')).\
                    annotate(s_inc=Sum('incarico__compenso_totale')).\
                    order_by('tipologia_partecipata')
                self.template_name = "nominati/part_tipologia.html"

            if tipologia == 'part_competenze':
                context['table'] = partecipate.order_by('-competenza_partecipata')
                self.template_name = "nominati/part_competenze.html"

            if tipologia == 'part_finalita':
                context['table'] = partecipate.order_by('-finalita_partecipata')
                self.template_name = "nominati/part_finalita.html"

            if tipologia == 'part_resoconto':
                partecipate_ids = partecipate.values_list('codice_fiscale')
                bilancio_part={}
                for b in Bilancio.objects.filter(partecipata_cf__codice_fiscale__in=partecipate_ids):
                    if b.partecipata_cf not in bilancio_part:
                        bilancio_part[b.partecipata_cf] = b
                    elif b.resoconto is not None and b.anno > bilancio_part[b.partecipata_cf].anno:
                        bilancio_part[b.partecipata_cf] = b

                context['table']=sorted(bilancio_part.values(),key=lambda bilancio: bilancio.resoconto)
                self.template_name = "nominati/part_resoconto.html"

            if tipologia == 'amm_tot':

                context['n_amministratori_uomini'] = incarichi.filter(persona__sesso=1).values('persona').distinct().count()
                context['n_amministratori_donne'] = incarichi.filter(persona__sesso=0).values('persona').distinct().count()
                context['n_amministratori'] =context['n_amministratori_donne']+context['n_amministratori_uomini']

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

                context['table'] = incarichi.\
                    filter(persona__openpolis_id__isnull=False).\
                    exclude(persona__openpolis_id='').\
                    order_by('persona__cognome').distinct()

                self.template_name = 'nominati/amm_politici.html'

            if tipologia == 'amm_incarichi':

                context['table'] = incarichi.\
                    values('persona', 'persona__nome', 'persona__cognome').\
                    annotate(n=Count('persona')).order_by('-n')

                self.template_name = 'nominati/amm_incarichi.html'

            if tipologia == 'amm_compenso':

                context['table'] = incarichi.\
                    values('persona', 'persona__nome', 'persona__cognome').\
                    annotate(s=Sum('compenso_totale')).order_by('-s')

                self.template_name = 'nominati/amm_compenso.html'

            if tipologia == 'lista_nominati':

                lista_nominati = incarichi.\
                    select_related('persona', 'tipo_carica', 'partecipata_cf', 'ente_nominante_cf').\
                    annotate(nInc = Count('persona__incarico')).\
                    order_by('persona__cognome')

                context['table']=lista_nominati
                self.template_name = 'nominati/lista_nominati.html'

        return context





class RegioneDetailView(PartecipateView, DetailView):
    model = Regione
    context_object_name = "regione"
    base_template='nominati/regione_detail.html'


    def get_context_data(self, **kwargs ):
        r = self.get_object()
        now = datetime.now()
        self.partecipate = Partecipata.objects.all().filter(ente__regione = r).select_related().distinct()
        self.incarichi = Incarico.objects.filter(ente_nominante_cf__regione = r).\
            filter(Q(data_inizio__lte=now) &
                   (Q(data_fine__gte=now) | Q(data_fine__isnull=True)))
        self.context = super(RegioneDetailView, self).get_context_data(**kwargs)

        return self.context


class NazioneView(PartecipateView, TemplateView):

    template_name='nominati/nazione_detail.html'


    def get_context_data(self, **kwargs):

        now = datetime.now()
        self.base_template = self.template_name
        self.partecipate =  Partecipata.objects.all().select_related().distinct()

        tipologia = self.request.GET.get('tipo',)
        if tipologia == 'amm_compenso':

            self.incarichi= Incarico.objects.all().\
                filter(Q(data_inizio__lte=now) &
                       (Q(data_fine__gte=now) | Q(data_fine__isnull=True))).\
                values('persona', 'persona__nome', 'persona__cognome').\
                annotate(s=Sum('compenso_totale')).filter(s__gte=100000).order_by('-s')

        elif tipologia =='amm_incarichi':
            self.incarichi = Incarico.objects.all().\
                filter(Q(data_inizio__lte=now) &
                       (Q(data_fine__gte=now) | Q(data_fine__isnull=True))).\
                values('persona', 'persona__nome', 'persona__cognome').\
                annotate(n=Count('persona')).filter(n__gt=2).order_by('-n')

        else:
            self.incarichi = Incarico.objects.all().\
                    filter(Q(data_inizio__lte=now) &
                           (Q(data_fine__gte=now) | Q(data_fine__isnull=True)))

        self.context = super(NazioneView, self).get_context_data(**kwargs)
        self.context['n_partecipate'] = self.partecipate.count()
        return self.context


class EnteDetailView(PartecipateView, DetailView):
    model = Ente
    context_object_name = "ente"
    queryset = Ente.objects.all()
    base_template='nominati/ente_detail.html'

    def get_context_data(self, **kwargs):
        e = self.get_object()
        now = datetime.now()
        self.partecipate = Partecipata.objects.all().filter(ente__codice_fiscale=e.codice_fiscale).select_related().distinct()
        self.incarichi = Incarico.objects.filter(ente_nominante_cf=e.codice_fiscale).\
            filter(Q(data_inizio__lte=now) &
                   (Q(data_fine__gte=now) | Q(data_fine__isnull=True)))
        self.context = super(EnteDetailView, self).get_context_data(**kwargs)

        return self.context

class EnteJSONListView(JSONResponseMixin, EnteListView):
    def convert_context_to_json(self, context):
        return dumps(context['ente_list'])


class MergePersona_OP(View):

    def post(self, *args, **kwargs):
        #set the attrib openpolis_id for the selected persona
        if self.request.POST is not None:
            post = self.request.POST
            persona_id = post['persona_id']
            p = Persona.objects.get(pk=persona_id)
            p.openpolis_id = post['openpolis_id']
            p.save()
        return redirect(post['return_page'])


class RemovePersona_OP(View):

    def post(self, *args, **kwargs):
        #remove the attrib openpolis_id for the selected persona
        if self.request.POST is not None:
            post = self.request.POST
            persona_id = post['persona_id']
            p = Persona.objects.get(pk=persona_id)
            p.openpolis_id = None
            p.save()
        return redirect(post['return_page'])

def home(request):
    if request.user.is_authenticated():
        return render_to_response('nominati/home.html')
    else:
        return redirect('login/?next=/')

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


