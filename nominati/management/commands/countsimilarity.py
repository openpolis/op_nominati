# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError, LabelCommand
from django.conf import settings
import urllib2
from django.utils.http import urlencode
import json
import logging

from nominati.models import Persona


class Command(LabelCommand):
    """
    Task per contare le similarità delle persone con i dati di openpolis.
    """
    help = "Conta le similarità in openpolis per le persone inserite"

    option_list = BaseCommand.option_list

    args = '<persona_id>'
    label = 'identificativo persona'
    logger = logging.getLogger('countsimilarity')

    def handle(self, *labels, **options):
        self.logger.info("Inizio script")

        if not labels:
            persons = Persona.objects.all()
        else:
            persons = Persona.objects.filter(pk__in=labels)

        for persona in persons:
            self.handle_label(persona, **options)
        self.logger.info("Fine script")


    def handle_label(self, persona, **options):

        # build similarity url
        parameters = [
            ('first_name', persona.nome),
            ('last_name', persona.cognome)
        ]
        if persona.data_nascita:
            parameters.append(
                ('birth_date', persona.data_nascita)
            )

        op_similarity_url = "%s/?count=true&%s" %\
                            (settings.OP_API_SIMILARITY_BASE_URL, urlencode(parameters))
        self.logger.debug("url: %s" % op_similarity_url)

        json_data = self.get_json_response(op_similarity_url)
        try:
            self.logger.info("n politici simili: %s" % json_data)
            n_similars = int(json_data)
            persona.openpolis_n_similars = n_similars
            persona.save()
        except ValueError as e:
            if 'error' in json_data:
                self.logger.error("%s" % json_data['error'])
            else:
                self.logger.error("%s" % e)

    def get_json_response(self, url):
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
