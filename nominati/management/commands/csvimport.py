# -*- coding: utf-8 -*-
from _csv import QUOTE_MINIMAL, QUOTE_NONE
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError, LabelCommand
from django.conf import settings
import urllib2
from django.utils.http import urlencode
import codecs
import csv
from optparse import make_option
import logging
from nominati import utils
from nominati.models import Persona, Ente, Partecipata, Partecipazione, Regione, Comparto, TipologiaPartecipata
import pprint
from nominati.utils import UnicodeDictWriter


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
    unicode_writer = None
    logger = logging.getLogger('csvimport')
    errors_list = []


    def handle(self, *args, **options):

        if options['csvfile'] is None:
            self.logger.error("Csv file is needed\n")
            exit(1)

        if options['year'] is None:
            self.logger.error("Year value is needed\n")
            exit(1)

        self.csv_file = options['csvfile']
        self.logger.info('CSV FILE "%s"\n' % self.csv_file )

        # read csv file
        try:
            self.unicode_reader = \
                utils.UnicodeDictReader(open(self.csv_file, 'rU'),
                                        encoding=self.encoding,
                                        dialect="excel",
                                        escapechar  = None,
                                        lineterminator = '\r\n',
                                        quotechar=None,
                                        delimiter=';',
                                        quoting=QUOTE_NONE)
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


    def handle_rapp(self, *args, **options):
        exit(1)


    def handle_part(self, *args, **options):

        c = 0

        if options['delete']:
            self.logger.info("Erasing the precedently stored data...")
            Partecipazione.objects.filter(anno=options['year']).delete()

        self.logger.info("Inizio import da %s" % self.csv_file)

        for r in self.unicode_reader:

        # Totale:
        # COMPARTO_PA;REGIONE_PA;CODICE_FISCALE_PA;DENOMINAZIONE_PA;
        # CODICE_FISCALE_CONS_SOC;DENOMINAZIONE_CONS_SOC;
        # MACRO TIPOLOGIA;TIPOLOGIA SOCIETA;
        # ONERE COMPLESSIVO;PERCENTUALE PARTECIPAZIONE;DICHIARAZIONE INVIATA

            updated = False
            correct_ente = False
            correct_partecipata = False

            # zero padding for codice fiscale
            cf_ente = r['CODICE_FISCALE_PA'].zfill(11)
            cf_partecipata = r['CODICE_FISCALE_CONS_SOC'].zfill(11)

            # finds Ente in the DB
            try:
                ente = Ente.objects.get(codice_fiscale=cf_ente)
            except ObjectDoesNotExist:
                # se non esiste ente, stampo un warning e inserisco l'ente
                self.logger.info("%s: Ente non presente, aggiungo: %s" % ( cf_ente,r['DENOMINAZIONE_PA']))

                ente = Ente()
                ente.codice_fiscale = cf_ente
                ente.denominazione = r['DENOMINAZIONE_PA']

                try:
                    regione = Regione.objects.get(denominazione=r['REGIONE_PA'])
                except ObjectDoesNotExist:
                    self.logger.error("%s: Regione non presente, impossibile aggiungere il record con cf: %s" % ( c, r['CODICE_FISCALE_PA']))
                    self.errors_list.append({'line':str(c),'ente_cf':str(cf_ente), 'partecipata_cf': str(cf_partecipata),'type':'Regione non presente', 'data': r['REGIONE_PA']})
                else:
                    ente.regione = regione
                    try:
                        comparto = Comparto.objects.get(denominazione=r['COMPARTO_PA'])
                    except ObjectDoesNotExist:
                        self.logger.error("%s: Comparto non presente, impossibile aggiungere il record con cf: %s" % ( c, r['CODICE_FISCALE_PA']))
                        self.errors_list.append({'line':str(c),'ente_cf':str(cf_ente), 'partecipata_cf': str(cf_partecipata),'type':'Comparto non presente','data': r['COMPARTO_PA']})
                    else:
                        ente.comparto=comparto
                        # insert new Ente obj
                        self.logger.info("%s: Ente inserito: %s" % ( cf_ente,r['DENOMINAZIONE_PA']))
                        ente.save()
                        correct_ente = True

            else:
                self.logger.info("%s: Ente presente: %s" % ( cf_ente,r['DENOMINAZIONE_PA']))
                correct_ente = True

            # if ente exists or has been inserted correctly checks if the partecipata is already present
            # otherwise it will be inserted in the db
            if correct_ente:

                try:
                    partecipata = Partecipata.objects.get(codice_fiscale=cf_partecipata)
                except ObjectDoesNotExist:
                    #     if partecipata is not present, insert new Partecipata
                    partecipata = Partecipata()
                    partecipata.codice_fiscale=cf_partecipata
                    partecipata.denominazione=r['DENOMINAZIONE_CONS_SOC']
                    macro_tipologia = r['MACRO TIPOLOGIA']
                    if macro_tipologia == 'SOCIETA':
                        macro_tipologia = 'SOCIETA\''
                    if macro_tipologia in dict(Partecipata.MACRO_TIPOLOGIA):
                        partecipata.macro_tipologia = macro_tipologia

                        # checks for tipologia partecipata
                        r_tipologia_partecipata=r['TIPOLOGIA SOCIETA']

                        # correction for errors in the csv
                        if r_tipologia_partecipata == 'Societ� S.r.l.'.decode('utf-8') \
                            or r_tipologia_partecipata == 'Societï¿½ S.r.l.'.decode('utf-8'):
                            r_tipologia_partecipata = 'Società S.r.l.'
                        if r_tipologia_partecipata == 'Societ� S.p.a.'.decode('utf-8')\
                            or r_tipologia_partecipata == 'Societï¿½ S.p.a.':
                            r_tipologia_partecipata = 'Società S.p.a.'
                        if r_tipologia_partecipata == 'Societï¿½ di Trasformazione Urbana'.decode('utf-8'):
                            r_tipologia_partecipata = 'Società di Trasformazione Urbana'
                        if r_tipologia_partecipata == 'Azienda Speciale'.decode('utf-8'):
                            r_tipologia_partecipata = 'Azienda speciale'
                        if r_tipologia_partecipata == 'ALTRO TIPO DI SOCIETA\''.decode('utf-8'):
                            r_tipologia_partecipata = 'Altro tipo di società'

                        try:
                            tipologia_partecipata = TipologiaPartecipata.objects.get(denominazione=r_tipologia_partecipata)
                        except ObjectDoesNotExist:
                            self.logger.error("%s: Tipologia Partecipata non presente, impossibile aggiungere il record con cf: %s" % ( c, r['CODICE_FISCALE_PA']))
                            self.errors_list.append({'line':str(c),'ente_cf':str(cf_ente), 'partecipata_cf': str(cf_partecipata),'type':'Tipologia Partecipata non presente', 'data':r_tipologia_partecipata})
                        else:
                            # inserts the new partecipata
                            partecipata.tipologia_partecipata = tipologia_partecipata
                            partecipata.save()
                            self.logger.info("%s: Partecipata inserita: %s" % ( cf_partecipata,r['DENOMINAZIONE_CONS_SOC']))
                            correct_partecipata = True
                    else:
                        self.logger.error("%s: Macro Tipologia non presente, impossibile aggiungere il record con cf: %s" % ( c, r['CODICE_FISCALE_PA']))
                        self.errors_list.append({'line':str(c),'ente_cf':str(cf_ente), 'partecipata_cf': str(cf_partecipata),'type':'Macro Tipologia non presente', 'data':macro_tipologia})

                else:
                    correct_partecipata = True

                # if ente is correct and partecipata is correct, inserts the new partecipazioni data
                if correct_partecipata:

                    partecipazione = None
                    try:
                        partecipazione = \
                            Partecipazione.objects. \
                                get(anno=options['year'],
                                    ente_cf=ente,
                                    partecipata_cf=partecipata
                            )

                    except ObjectDoesNotExist:
                        pass

                    # if update is true we update existing records about partecipazione
                    if options['update'] is True and partecipazione is not None:
                        partecipazione.onere_complessivo = r['ONERE COMPLESSIVO']
                        partecipazione.percentuale_partecipazione = r['PERCENTUALE PARTECIPAZIONE']
                        partecipazione.dichiarazione_inviata = r['DICHIARAZIONE INVIATA']
                        partecipazione.save()
                        self.logger.info("%s: Partecipazione aggiornata: %s" % ( c,r['DENOMINAZIONE_CONS_SOC']))
                    else:
                        if options['update'] is False and partecipazione is not None:
                            self.logger.error("%s: Partecipazione gia presente, impossibile aggiungere il record con cf: %s" % ( c, r['CODICE_FISCALE_PA']))
                            self.errors_list.append({'line':str(c),'ente_cf':str(cf_ente), 'partecipata_cf': str(cf_partecipata),'type':'Partecipazione gia presente', 'data':''})
                        else:
                            
                            # if the obj doesnt exists the new partecipazione is created
                            partecipazione = Partecipazione()
                            partecipazione.anno = options['year']
                            partecipazione.partecipata_cf = partecipata
                            partecipazione.ente_cf = ente
                            partecipazione.onere_complessivo = r['ONERE COMPLESSIVO']
                            partecipazione.percentuale_partecipazione = r['PERCENTUALE PARTECIPAZIONE']
                            partecipazione.dichiarazione_inviata = r['DICHIARAZIONE INVIATA']
                            partecipazione.save()
                            self.logger.info("%s: Partecipazione inserita: %s" % ( c,r['DENOMINAZIONE_CONS_SOC']))

            c += 1

        if len(self.errors_list)>0:
            self.logger.info("Inizio a scrivere il file di log degli errori part_error.log")
            self.unicode_writer = \
                utils.UnicodeDictWriter(open("part_error.log", 'w'),
                                        fieldnames = ['line','ente_cf','partecipata_cf','type','data'],
                                        encoding=self.encoding,
                                        dialect="excel",
                                        escapechar  = "\\",
                                        lineterminator = '\r\n',
                                        quotechar='"',
                                        delimiter=',',
                                        quoting=QUOTE_MINIMAL)


            self.unicode_writer.writerows(self.errors_list)

            self.logger.info("Fine scrittura")



