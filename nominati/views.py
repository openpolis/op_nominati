from django.http import HttpResponse

from django.conf import settings
import urllib2
from django.utils.http import urlencode
import json
import logging

from nominati.models import Persona

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