#!/usr/bin/python
# -*- coding: utf-8 -*-

from model_utils import Choices
from model_utils.managers import PassThroughManager
from nominati.managers import TimeFramedQuerySet
from django.utils.functional import cached_property
from django.db import models
from django.db.models import Sum
from django.db.models.query_utils import Q
from datetime import datetime

class Comparto(models.Model):
    denominazione = models.CharField(max_length=255)

    def __unicode__(self):
        return self.denominazione

    class Meta:
        verbose_name_plural = u'Comparti'

class Cpt_Settore(models.Model):
    denominazione = models.CharField(max_length=255)
    codice = models.CharField(max_length=10)

class Cpt_Settore_Partecipata(models.Model):
    partecipata = models.ForeignKey('Partecipata', on_delete=models.SET_DEFAULT, null=False, default='')
    settore = models.ForeignKey('Cpt_Settore', on_delete=models.SET_DEFAULT, null=False, default='')

class Cpt_Categoria(models.Model):
    denominazione = models.CharField(max_length=255)
    codice = models.CharField(max_length=3)

class Cpt_Sottocategoria(models.Model):
    denominazione = models.CharField(max_length=255)
    codice = models.CharField(max_length=1)
    categoria = models.ForeignKey('Cpt_Categoria', on_delete=models.CASCADE, null=False)

class Cpt_Sottotipo(models.Model):
    denominazione = models.CharField(max_length=255)
    codice = models.CharField(max_length=2)
    sottocategoria = models.ForeignKey('Cpt_Sottocategoria', on_delete=models.CASCADE, null=False)

class Partecipata(models.Model):
    codice_fiscale = models.CharField(max_length=11, primary_key=True)
    denominazione = models.CharField(max_length=255)
    MACRO_TIPOLOGIA = Choices(
        ('SOCIETA\'', 'Società'),
        ('CONSORZIO', 'Consorzio'),
        ('FONDAZIONE', 'Fondazione')
    )

    UNIVERSO_RIFERIMENTO = Choices(
        ('PA', 'PA'),
        ('ExtraPA', 'ExtraPA')
    )

    macro_tipologia = models.CharField(max_length=32, choices=MACRO_TIPOLOGIA)
    tipologia_partecipata = models.ForeignKey('TipologiaPartecipata', null=True, on_delete=models.PROTECT)
    competenza_partecipata = models.ForeignKey('CompetenzaPartecipata', null=True, on_delete=models.SET_NULL)
    finalita_partecipata = models.ForeignKey('FinalitaPartecipata', null=True, on_delete=models.SET_NULL)
    url = models.URLField(blank=True, null=True)
    indirizzo = models.CharField(max_length=100, null=True)
    cap = models.CharField(max_length=5, null=True)
    comune = models.CharField(max_length=50, null=True)
    provincia = models.CharField(max_length=3, null=True)
    regione = models.ForeignKey('Regione', on_delete=models.SET_NULL, null=True)
    cpt_universo_riferimento = models.CharField(max_length=8, choices=UNIVERSO_RIFERIMENTO, null=True)
    cpt_primo_anno_rilevazione = models.CharField(max_length=5, null=True, blank=True, default=None)
    cpt_ultimo_anno_rilevazione = models.CharField(max_length=5, null=True, blank=True, default=None)

    @cached_property
    def ultimo_bilancio(self):
        bilanci = self.bilancio_set.all().order_by('-anno')[:1]
        return bilanci[0] if len(bilanci) else None

    @property
    def numero_incarichi_attivi(self):
        now = datetime.now()
        return self.incarico_set.filter(
            Q(data_inizio__lte=now) & 
            (Q(data_fine__gte=now) | Q(data_fine__isnull=True))).count()
        
    @property
    def totale_compensi_incarichi_attivi(self):
        now = datetime.now()
        return self.incarico_set.filter(
            Q(data_inizio__lte=now) & 
            (Q(data_fine__gte=now) | Q(data_fine__isnull=True))).aggregate(s=Sum('compenso_totale'))['s']

    def __unicode__(self):
        return self.denominazione

    class Meta:
        verbose_name_plural = u'Partecipate'

class TipologiaPartecipata(models.Model):
    denominazione = models.CharField(max_length=255)

    def __unicode__(self):
        return self.denominazione

    class Meta:
        verbose_name_plural = u'Tipologie partecipate'


class CompetenzaPartecipata(models.Model):
    denominazione = models.CharField(max_length=255)

    @property
    def finalita(self):
        return self.finalitapartecipata_set.all()

    def __unicode__(self):
        return self.denominazione

    class Meta:
        verbose_name_plural = u'Competenze partecipate'

class FinalitaPartecipata(models.Model):
    denominazione = models.CharField(max_length=255)
    competenza_partecipata = models.ManyToManyField(CompetenzaPartecipata, db_table='nominati_competenza_finalita')

    def __unicode__(self):
        return self.denominazione

    class Meta:
        verbose_name_plural = u'Finalità partecipate'


class Bilancio(models.Model):
    RESOCONTO = Choices(
        (0, 'Pareggio'),
        (1, 'Avanzo'),
        (-1, 'Perdita')
    )

    anno = models.CharField(max_length=4)
    resoconto = models.IntegerField(choices=RESOCONTO)
    dettaglio = models.IntegerField(blank=True, null=True)
    partecipata_cf = models.ForeignKey('Partecipata', db_column='partecipata_cf')

    class Meta:
        verbose_name_plural = u'Bilanci'

class Incarico(models.Model):
    persona = models.ForeignKey('Persona')
    ente_nominante_cf = models.ForeignKey('Ente', verbose_name=u'Ente', db_column='ente_cf', blank=True, null=True)
    tipo_carica = models.ForeignKey('TipoCarica')
    partecipata_cf = models.ForeignKey('Partecipata', db_column='partecipata_cf', verbose_name=u'Partecipata', blank=True, null=True)
    compenso_anno = models.IntegerField(verbose_name=u'Comp. anno', null=True, blank=True)
    compenso_carica = models.IntegerField(verbose_name=u'Comp. carica', null=True, blank=True)
    altri_compensi = models.IntegerField(verbose_name=u'Altri comp.', null=True, blank=True)
    compenso_totale = models.IntegerField(verbose_name=u'Comp. TOT', null=True, blank=True)
    indennita_risultato = models.IntegerField(verbose_name=u'Ind. risultato', null=True, blank=True)
    data_inizio = models.DateField(null=True, blank=True)
    data_fine = models.DateField(null=True, blank=True)
    objects = PassThroughManager.for_queryset_class(TimeFramedQuerySet)()

    def save(self, *args, **kwargs):

        self.compenso_totale = 0
        if self.compenso_anno:
            self.compenso_totale += self.compenso_anno
        if self.compenso_carica:
            self.compenso_totale += self.compenso_carica
        if self.indennita_risultato:
            self.compenso_totale += self.indennita_risultato
        if self.altri_compensi:
            self.compenso_totale += self.altri_compensi
        if self.indennita_risultato is None and self.compenso_anno is None \
           and self.compenso_carica is None and self.compenso_carica is None \
          and self.altri_compensi is None:
            self.compenso_totale = None

        # Call parent's ``save`` function
        super(Incarico, self).save(*args, **kwargs)



    class Meta:
        verbose_name_plural = u'Incarichi'

class Ente(models.Model):
    codice_fiscale = models.CharField(max_length=11, primary_key=True)
    denominazione = models.CharField(max_length=255)
    regione = models.ForeignKey('Regione')
    comparto = models.ForeignKey('Comparto')
    partecipata_set = models.ManyToManyField('Partecipata', through='Partecipazione')

    @property
    def partecipate(self):
        return self.partecipata_set.all()

    @property
    def n_partecipate(self):
        return self.partecipata_set.count()

    def __unicode__(self):
        return self.denominazione

    class Meta:
        verbose_name_plural = u'Enti'

class Partecipazione(models.Model):
    SENT = Choices(
        ('SI', u'Sì'),
        ('NO', u'No'),
    )
    ente_cf = models.ForeignKey('Ente', verbose_name=u'Ente', db_column='ente_cf')
    partecipata_cf = models.ForeignKey('Partecipata', verbose_name=u'Partecipata', db_column='partecipata_cf')
    anno = models.CharField(max_length=4) 
    onere_complessivo = models.CharField(max_length=255, blank=True)
    percentuale_partecipazione = models.CharField(max_length=255, blank=True)
    dichiarazione_inviata = models.CharField(max_length=2, choices=SENT, blank=True)


    class Meta:
        verbose_name = u'Partecipazione'
        verbose_name_plural = u'Partecipazioni'


class Persona(models.Model):
    FEMALE_SEX = 0
    MALE_SEX = 1
    SEX = Choices(
        (MALE_SEX, 'Uomo'),
        (FEMALE_SEX, 'Donna'),
    )

    nome = models.CharField(max_length=64)
    cognome = models.CharField(max_length=64)
    data_nascita = models.DateField(null=True, blank=True, verbose_name='Data di nascita')
    luogo_nascita = models.CharField(max_length=64, null=True, blank=True,verbose_name='Luogo nasc')
    sesso = models.IntegerField(choices=SEX, blank=True)
    openpolis_id = models.CharField(max_length=10, null=True, blank=True, verbose_name='op_id')
    openpolis_n_similars = models.IntegerField(default=0,verbose_name=u"n_similars")

    @property
    def incarichi(self):
        return self.incarico_set.all()

    @property
    def op_id(self):
        if self.openpolis_id !=  '' and self.openpolis_id is not None:
            return int(self.openpolis_id)
        else:
            return None

    def __unicode__(self):
        return self.nome + " " + self.cognome

    def has_op_id(self):
        return True if self.openpolis_id else False;


    class Meta:
        verbose_name_plural = u'Persone'
        unique_together = ('nome', 'cognome', 'data_nascita', 'luogo_nascita')

class Regione(models.Model):
    denominazione = models.CharField(max_length=32)

    def __unicode__(self):
        return self.denominazione

    @property
    def n_partecipate(self):
        return Partecipata.objects.filter(ente__regione = self._get_pk_val()).distinct().count()

    class Meta:
        verbose_name_plural = u'Regioni'

class TipoCarica(models.Model):
    denominazione = models.CharField(max_length=64)
    descrizione = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.denominazione

    class Meta:
        verbose_name = u'Tipo incarico'
        verbose_name_plural = u'Tipi incarico'

