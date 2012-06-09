from django.http import HttpResponse, HttpResponseNotFound
from django.core.serializers import serialize
from django.conf import settings
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.db.models.query import QuerySet
from django.utils.functional import curry

from nominati.models import Ente
import json
from json.encoder import JSONEncoder
import urllib2

from nominati.models import Persona, Ente

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

class EnteListView(ListView):
    model = Ente

    def get_queryset(self):
        if 'qterm' in self.request.GET:
            qterm = self.request.GET['qterm']
            return Ente.objects.filter(denominazione__icontains=qterm)[0:50]
        else:
            return Ente.objects.all()[0:50]


class EnteJSONListView(JSONResponseMixin, EnteListView):
    def convert_context_to_json(self, context):
        return dumps(context['ente_list'])


class EnteDetailView(DetailView):
    model = Ente
    context_object_name = "ente"
    queryset = Ente.objects.all()

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