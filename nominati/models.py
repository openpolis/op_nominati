#!/usr/bin/python
# -*- coding: utf-8 -*-

from model_utils import Choices

from django.db import models

class Comparto(models.Model):
    nome = models.CharField(max_length=255)

    def __unicode__(self):
        return self.nome

    class Meta:
        verbose_name_plural = u'Comparti'

class Partecipata(models.Model):
    MACRO_TIPOLOGIA = Choices(
        ('SOCIETA\'', 'Società'),
        ('CONSORZIO', 'Consorzio'),
        ('FONDAZIONE', 'Fondazione')
    )

    codice_fiscale = models.CharField(max_length=11, primary_key=True)
    denominazione = models.CharField(max_length=255)
    macro_tipologia = models.CharField(max_length=32, choices=MACRO_TIPOLOGIA)
    tipologia_partecipata = models.ForeignKey('TipologiaPartecipata')
    competenza_partecipata = models.ForeignKey('CompetenzaPartecipata', null=True)
    url = models.URLField(blank=True, null=True)

    @property
    def ultimo_bilancio(self):
        bilanci = self.bilancio_set.all().order_by('-anno')
        return bilanci[0] if len(bilanci) else None

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

    def __unicode__(self):
        return self.denominazione

    class Meta:
        verbose_name_plural = u'Competenze partecipate'

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
    ente_nominante_cf = models.ForeignKey('Ente', verbose_name=u'Ente', db_column='ente_cf')
    tipo_carica = models.ForeignKey('TipoCarica')
    partecipata_cf = models.ForeignKey('Partecipata', db_column='partecipata_cf', verbose_name=u'Partecipata', blank=True, null=True)
    compenso_anno = models.IntegerField(verbose_name=u'Comp. anno', null=True, blank=True)
    compenso_carica = models.IntegerField(verbose_name=u'Comp. carica', null=True, blank=True)
    altri_compensi = models.IntegerField(verbose_name=u'Altri comp.', null=True, blank=True)
    compenso_totale = models.IntegerField(verbose_name=u'Comp. TOT', null=True, blank=True)
    indennita_risultato = models.IntegerField(verbose_name=u'Ind. risultato', null=True, blank=True)
    data_inizio = models.DateField(null=True, blank=True)
    data_fine = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):

        self.compenso_totale = 0
        if self.compenso_anno:
            self.compenso_totale += self.compenso_anno
        if self.compenso_carica:
            self.compenso_totale += self.compenso_carica
        if self.altri_compensi:
            self.compenso_totale += self.altri_compensi
        if self.compenso_totale is 0:
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
    data_nascita = models.DateField(null=True, blank=True)
    luogo_nascita = models.CharField(max_length=64, null=True, blank=True)
    sesso = models.IntegerField(choices=SEX, blank=True)
    openpolis_id = models.CharField(max_length=10, null=True, blank=True)
    openpolis_n_similars = models.IntegerField(default=0)

    def __unicode__(self):
        return self.nome + " " + self.cognome

    def has_openpolis_id(self):
        return True if self.openpolis_id else False;

    class Meta:
        verbose_name_plural = u'Persone'
        unique_together = ('nome', 'cognome', 'data_nascita', 'luogo_nascita')

class Regione(models.Model):
    nome = models.CharField(max_length=32)

    def __unicode__(self):
        return self.nome

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

