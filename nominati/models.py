#!/usr/bin/python
# -*- coding: utf-8 -*-

from model_utils import Choices

from django.db import models

class Comparto(models.Model):
    nome = models.CharField(max_length=255)

    def __unicode__(self):
        return self.nome

    class Meta:
        db_table = u'comparto'
        verbose_name_plural = u'Comparti'

class Ente(models.Model):
    MACRO_TIPOLOGIA = Choices(
        ('SOCIETA\'', 'Società'),
        ('CONSORZIO', 'Consorzio'),
        ('FONDAZIONE', 'Fondazione')
    )

    codice_fiscale = models.CharField(max_length=11, primary_key=True)
    denominazione = models.CharField(max_length=255)
    macro_tipologia = models.CharField(max_length=32, choices=MACRO_TIPOLOGIA)
    tipologia_ente = models.ForeignKey('TipologiaEnte', db_column='tipologia_ente')
    url = models.URLField(blank=True, null=True)

    def __unicode__(self):
        return self.denominazione

    class Meta:
        db_table = u'ente'
        verbose_name_plural = u'Enti'

class TipologiaEnte(models.Model):
    denominazione = models.CharField(max_length=255)

    def __unicode__(self):
        return self.denominazione

    class Meta:
        db_table = u'tipologia_ente'
        verbose_name_plural = u'Tipologie enti'

class Bilancio(models.Model):
    RESOCONTO = Choices(
        (0, 'Pareggio'),
        (1, 'Avanzo'),
        (-1, 'Perdita')
    )

    anno = models.CharField(max_length=4)
    resoconto = models.IntegerField(choices=RESOCONTO)
    dettaglio = models.IntegerField(blank=True, null=False)
    ente_cf = models.ForeignKey('Ente', db_column='ente_cf')

    class Meta:
        verbose_name_plural = u'Bilanci'

class Incarico(models.Model):
    persona = models.ForeignKey('Persona')
    istituzione_cf = models.ForeignKey('Istituzione', verbose_name=u'Istituzione', db_column='istituzione_cf')
    tipo_carica = models.ForeignKey('TipoCarica')
    ente_cf = models.ForeignKey('Ente', db_column='ente_cf', verbose_name=u'Ente', blank=True, null=True)
    compenso_anno = models.IntegerField(verbose_name=u'Comp. anno', null=True, blank=True)
    compenso_carica = models.IntegerField(verbose_name=u'Comp. carica', null=True, blank=True)
    altri_compensi = models.IntegerField(verbose_name=u'Altri comp.', null=True, blank=True)
    indennita_risultato = models.IntegerField(verbose_name=u'Ind. risult.', null=True, blank=True)
    data_inizio = models.DateField(null=True, blank=True)
    data_fine = models.DateField(null=True, blank=True)
    class Meta:
        db_table = u'incarico'
        verbose_name_plural = u'Incarichi'

class Istituzione(models.Model):
    codice_fiscale = models.CharField(max_length=11, primary_key=True)
    denominazione = models.CharField(max_length=255)
    regione = models.ForeignKey('Regione')
    comparto = models.ForeignKey('Comparto')
    ente_set = models.ManyToManyField('Ente', through='IstituzioneHasEnte')

    @property
    def enti_partecipati(self):
        return self.ente_set.all()

    def __unicode__(self):
        return self.denominazione

    class Meta:
        db_table = u'istituzione'
        verbose_name_plural = u'Istituzioni'

class IstituzioneHasEnte(models.Model):
    istituzione_cf = models.ForeignKey('Istituzione', verbose_name=u'Istituzione', db_column='istituzione_cf')
    ente_cf = models.ForeignKey('Ente', verbose_name=u'Ente', db_column='ente_cf')
    anno = models.CharField(max_length=4) 
    onere_complessivo = models.CharField(max_length=255, blank=True)
    percentuale_partecipazione = models.CharField(max_length=255, blank=True)
    dichiarazione_inviata = models.CharField(max_length=255, blank=True)
    class Meta:
        db_table = u'istituzione_has_ente'
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
    sesso = models.IntegerField(choices=SEX, blank=True)

    def __unicode__(self):
        return self.nome + " " + self.cognome

    class Meta:
        db_table = u'persona'
        verbose_name_plural = u'Persone'
        unique_together = ('nome', 'cognome', 'data_nascita')

class Regione(models.Model):
    nome = models.CharField(max_length=32)

    def __unicode__(self):
        return self.nome

    class Meta:
        db_table = u'regione'
        verbose_name_plural = u'Regioni'

class TipoCarica(models.Model):
    denominazione = models.CharField(max_length=64)
    descrizione = models.CharField(max_length=255, blank=True)
    class Meta:
        db_table = u'tipo_carica'
        verbose_name = u'Tipo incarico'
        verbose_name_plural = u'Tipo incarichi'

