# -*- coding: utf-8 -*-
from _csv import QUOTE_MINIMAL, QUOTE_NONE
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError, LabelCommand
from django.conf import settings
import csv
from optparse import make_option
import logging
from nominati import utils
from nominati.models import Persona, Ente, Partecipata, Partecipazione, Regione, Comparto, TipologiaPartecipata
import pprint



class Command(BaseCommand):
    """
    Task per importare la lista di partecipazioni dal CSV del Ministero Pubblica Amministrazione
    e dati dal CPT
    """

    help = "Import dati partecipazioni da CSV del Ministero PA"

    option_list = BaseCommand.option_list + (
        make_option('--csv-file',
                    dest='csvfile',
                    default=None,
                    help='Select csv file'),
        make_option('--type',
                    dest='type',
                    default=None,
                    help='Type of import: part|cpt_part'),
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

        if options['type'] == 'part':
            self.handle_part(*args, **options)

        elif options['type'] == 'cpt_part':
            self.handle_cptpart(*args, **options)

        else:
            self.logger.error("Wrong type %s. Select among part,cpt_part." % options['type'])
            exit(1)


    def handle_cptpart(self, *args, **options):

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
        
        # Totale
        # CPT_Anno_Produzione_BancaDati
        # DESCRIZIONE_ENTE
        # IDFISC_ENTE
        # INDIRIZZO_ENTE
        # CAP
        # COMUNE
        # PROVINCIA
        # REGIONE
        # CPT_Universo_riferimento
        # CPT_COD_CATEGORIA
        # CPT_DESCR_CATEGORIA
        # CPT_COD_SOTTOTIPO
        # CPT_DESCR_SOTTOTIPO
        # CPT_Primo_Anno_Rilevazione
        # CPT_Ultimo_Anno_Rilevazione
        # CPT_Settore01 ... CPT_Settore12

        for r in self.unicode_reader:
            existing_partecipata = False

            # zero padding for codice fiscale
            cf_partecipata = r['IDFISC_ENTE'].zfill(11)

            #  if partecipata is not in the db, insert new Partecipata
            regione = None

            nome_regione = r['REGIONE']

            # fixes for CSV errors
            if nome_regione == 'Friuli Venezia Giulia':
                nome_regione='FRIULI-VENEZIA GIULIA'
            if nome_regione == 'Emilia Romagna':
                nome_regione='EMILIA-ROMAGNA'
            if nome_regione == 'Provincia Autonoma di Bolzano' or nome_regione == 'Provincia Autonoma di Trento':
                nome_regione='TRENTINO-ALTO ADIGE'

            try:
                regione = Regione.objects.get(denominazione=nome_regione.upper())
            except ObjectDoesNotExist:
                self.logger.error("%s: Regione non presente, impossibile aggiungere il record con cf: %s" % ( c, cf_partecipata))
                self.errors_list.append({'line':str(c),'partecipata_cf': str(cf_partecipata),'type':'Regione non presente', 'data': r['REGIONE']})
            else:

                partecipata, partecipata_created = Partecipata.objects.get_or_create(
                    codice_fiscale=cf_partecipata,
                    defaults={
                        'denominazione':r['DESCRIZIONE_ENTE'],
                        'indirizzo': r['INDIRIZZO_ENTE'],
                        'comune': r['COMUNE'],
                        'cap': r['CAP'],
                        'provincia': r['PROVINCIA'],
                        'regione': regione,
                        'cpt_universo_riferimento': r['CPT_Universo_riferimento'],
                        'cpt_primo_anno_rilevazione':r['CPT_Primo_Anno_Rilevazione'],
                        'cpt_ultimo_anno_rilevazione':r['CPT_Ultimo_Anno_Rilevazione']

                    }
                )

                if partecipata_created is True:
                    self.logger.info("%s: Partecipata inserita: %s" % ( cf_partecipata,r['DESCRIZIONE_ENTE']))
                else:
                    if options['update']:

                        partecipata.denominazione = r['DESCRIZIONE_ENTE']
                        partecipata.indirizzo = r['INDIRIZZO_ENTE']
                        partecipata.comune = r['COMUNE']
                        partecipata.cap = r['CAP']
                        partecipata.provincia = r['PROVINCIA']
                        partecipata.regione = regione
                        partecipata.cpt_universo_riferimento = r['CPT_Universo_riferimento']
                        partecipata.cpt_primo_anno_rilevazione = r['CPT_Primo_Anno_Rilevazione']
                        partecipata.cpt_ultimo_anno_rilevazione = r['CPT_Ultimo_Anno_Rilevazione']
                        partecipata.save()

                        self.logger.info("%s: Partecipata presente aggiornata: %s" % ( cf_partecipata,r['DESCRIZIONE_ENTE']))
                    else:
                        self.logger.info("%s: Partecipata presente: %s" % ( cf_partecipata,r['DESCRIZIONE_ENTE']))




            c=+1
            if c >= 100:
                break

        self.write_errorlog("cptpart_error.log", fieldnames = ['line','partecipata_cf','type','data'])
        exit(1)


    def handle_part(self, *args, **options):

        if self.csv_file=='':
            self.csv_file = './partecipazioni.csv'

        self.logger.info('CSV FILE "%s"\n' % self.csv_file )
        self.encoding='latin1'
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

        c = 0
        added_enti = 0
        added_partecipata = 0

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
                added_enti+=1

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
                            added_partecipata+=1
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

            self.write_errorlog("part_error.log", fieldnames = ['line','ente_cf','partecipata_cf','type','data'])

            if added_partecipata > 0:
                self.logger.info("Aggiunte %s nuove partecipate", added_partecipata)
            if added_enti> 0:
                self.logger.info("Aggiunti %s nuovi enti", added_enti)



    def write_errorlog(self, filename, fieldnames):

        if len(self.errors_list)>0:
            self.logger.info("Inizio a scrivere il file "+filename)
            self.unicode_writer = \
                utils.UnicodeDictWriter(open(filename, 'w'),
                                        fieldnames = fieldnames,
                                        encoding=self.encoding,
                                        dialect="excel",
                                        escapechar  = "\\",
                                        lineterminator = '\r\n',
                                        quotechar='"',
                                        delimiter=',',
                                        quoting=QUOTE_MINIMAL)


            self.unicode_writer.writerows(self.errors_list)
            self.logger.info("Fine scrittura file")