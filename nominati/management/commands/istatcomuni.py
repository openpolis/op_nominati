# -*- coding: utf-8 -*-
from _csv import QUOTE_MINIMAL, QUOTE_NONE
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.conf import settings
import csv
from optparse import make_option
import logging
from nominati import utils
from nominati.models import Ente
import pprint



class Command(BaseCommand):
    """
    Task per importare la lista di codici istat di comuni, province e regioni
    e dati dal CPT
    """

    help = "Import dati codici istat dei comuni, province e regioni"

    option_list = BaseCommand.option_list + (
        make_option('--csv-file',
                    dest='csvfile',
                    default=None,
                    help='Select csv file'),
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
    unicode_reader = None
    unicode_writer = None
    encoding = None
    logger = logging.getLogger('csvimport')
    errors_list = []


    def handle(self, *args, **options):

        if options['csvfile'] is None:
            self.logger.error("Csv file is needed\n")
            exit(1)

        self.csv_file = options['csvfile']
        self.handle_istat(*args, **options)


    def handle_istat(self, *args, **options):

        self.logger.info('CSV FILE "%s"\n' % self.csv_file )
        self.encoding='utf-8'
        # read csv file
        try:
            self.unicode_reader = \
                utils.UnicodeDictReader(open(self.csv_file, 'rU'),
                                        encoding=self.encoding,
                                        dialect="excel"
                )
        except IOError:
            self.logger.error("It was impossible to open file %s\n" % self.csv_file)
            exit(1)
        except csv.Error, e:
            self.logger.error("CSV error while reading %s: %s\n" % (self.csv_file, e.message))

        c = 0
        self.logger.info("Inizio import da %s" % self.csv_file)


        for r in self.unicode_reader:
            # zero padding for codice fiscale
            # cf_partecipata = r['IDFISC_ENTE'].zfill(11)
            ente = Ente.objects.get(codice_fiscale=r['codice_fiscale'])
            ente.codice_istat = r['istat'].zfill(6)
            ente.save()
            self.logger.info("%s: Aggiunto codice istat: %s" % ( ente.denominazione,r['istat'].zfill(6)))


