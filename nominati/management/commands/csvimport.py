# -*- coding: utf-8 -*-
from _csv import QUOTE_MINIMAL, QUOTE_NONE
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError, LabelCommand
from django.conf import settings
import urllib2
from django.utils.http import urlencode
import csv
from optparse import make_option
import logging
from nominati import utils
from nominati.models import Persona, Ente, Partecipata, Partecipazione
import pprint


class Command(BaseCommand):
    """
    Task per importare la lista di partecipazioni dal CSV del Ministero Pubblica Amministrazione
    """

    help = "Import dati partecipazioni da CSV del Ministero PA"

    option_list = BaseCommand.option_list + (
        make_option('--csv-file',
                    dest='csvfile',
                    default='./partecipazioni.csv',
                    help='Select csv file'),
        make_option('--type',
                    dest='type',
                    default=None,
                    help='Type of import: part|rapp'),
        make_option('--year',
                    dest='year',
                    default=None,
                    help='Year of import: eg.2012'),
        make_option('--update',
                    dest='update',
                    action='store_true',
                    default=False,
                    help='Update Existing Records: True|False'),
        make_option('--delete',
                    dest='delete',
                    action='store_true',
                    default=False,
                    help='Delete Existing Records: True|False'),
    )

    csv_file = ''
    encoding = 'latin1'
    unicode_reader = None
    logger = logging.getLogger('csvimport')


    def handle(self, *args, **options):

        if 'csvfile' not in options:
            self.logger.error("Csv file is needed\n")
            exit(1)

        self.csv_file = options['csvfile']
        self.logger.info('CSV FILE "%s"\n' % self.csv_file )

        # read csv file
        try:
            self.unicode_reader = \
                utils.UnicodeDictReader(open(self.csv_file, 'r'), encoding=self.encoding, dialect="excel", quotechar=None, delimiter=';', quoting=QUOTE_NONE)
        except IOError:
            self.logger.error("It was impossible to open file %s\n" % self.csv_file)
            exit(1)
        except csv.Error, e:
            self.logger.error("CSV error while reading %s: %s\n" % (self.csv_file, e.message))

        if options['type'] == 'part':
            self.handle_part(*args, **options)

        elif options['type'] == 'rapp':
            self.handle_rapp(*args, **options)

        else:
            self.logger.error("Wrong type %s. Select among part,rapp." % options['type'])
            exit(1)


    def handle_part(self, *args, **options):
        c = 0

        if options['delete']:
            self.logger.info("Erasing the precedently stored data...")
            Partecipazione.objects.filter(anno=options['year']).delete()

        self.logger.info("Inizio import da %s" % self.csv_file)

        for r in self.unicode_reader:
            pprint.pprint(r)

        # Totale:
        # COMPARTO_PA;REGIONE_PA;CODICE_FISCALE_PA;DENOMINAZIONE_PA;
        # CODICE_FISCALE_CONS_SOC;DENOMINAZIONE_CONS_SOC;
        # MACRO TIPOLOGIA;TIPOLOGIA SOCIETA;
        # ONERE COMPLESSIVO;PERCENTUALE PARTECIPAZIONE;DICHIARAZIONE INVIATA


        
