# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Comparto'
        db.create_table(u'comparto', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('nominati', ['Comparto'])

        # Adding model 'Ente'
        db.create_table(u'ente', (
            ('codice_fiscale', self.gf('django.db.models.fields.CharField')(max_length=11, primary_key=True)),
            ('denominazione', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('macro_tipologia', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('tipologia', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('nominati', ['Ente'])

        # Adding model 'Incarico'
        db.create_table(u'incarico', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('persona', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nominati.Persona'])),
            ('istituzione_cf', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nominati.Istituzione'], db_column='istituzione_cf')),
            ('tipo_carica', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nominati.TipoCarica'])),
            ('ente_cf', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nominati.Ente'], null=True, db_column='ente_cf', blank=True)),
            ('compenso_anno', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('compenso_carica', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('altri_compensi', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('indennita_risultato', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('data_inizio', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('data_fine', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('nominati', ['Incarico'])

        # Adding model 'Istituzione'
        db.create_table(u'istituzione', (
            ('codice_fiscale', self.gf('django.db.models.fields.CharField')(max_length=11, primary_key=True)),
            ('denominazione', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('regione', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nominati.Regione'])),
            ('comparto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nominati.Comparto'])),
        ))
        db.send_create_signal('nominati', ['Istituzione'])

        # Adding model 'IstituzioneHasEnte'
        db.create_table(u'istituzione_has_ente', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('istituzione_cf', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nominati.Istituzione'], db_column='istituzione_cf')),
            ('ente_cf', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nominati.Ente'], db_column='ente_cf')),
            ('anno', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('onere_complessivo', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('percentuale_partecipazione', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('dichiarazione_inviata', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('nominati', ['IstituzioneHasEnte'])

        # Adding model 'Persona'
        db.create_table(u'persona', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('cognome', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('data_nascita', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('sesso', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('nominati', ['Persona'])

        # Adding model 'Regione'
        db.create_table(u'regione', (
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
        ))
        db.send_create_signal('nominati', ['Regione'])

        # Adding model 'TipoCarica'
        db.create_table(u'tipo_carica', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('denominazione', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('descrizione', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('nominati', ['TipoCarica'])


    def backwards(self, orm):
        # Deleting model 'Comparto'
        db.delete_table(u'comparto')

        # Deleting model 'Ente'
        db.delete_table(u'ente')

        # Deleting model 'Incarico'
        db.delete_table(u'incarico')

        # Deleting model 'Istituzione'
        db.delete_table(u'istituzione')

        # Deleting model 'IstituzioneHasEnte'
        db.delete_table(u'istituzione_has_ente')

        # Deleting model 'Persona'
        db.delete_table(u'persona')

        # Deleting model 'Regione'
        db.delete_table(u'regione')

        # Deleting model 'TipoCarica'
        db.delete_table(u'tipo_carica')


    models = {
        'nominati.comparto': {
            'Meta': {'object_name': 'Comparto', 'db_table': "u'comparto'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'nominati.ente': {
            'Meta': {'object_name': 'Ente', 'db_table': "u'ente'"},
            'codice_fiscale': ('django.db.models.fields.CharField', [], {'max_length': '11', 'primary_key': 'True'}),
            'denominazione': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'macro_tipologia': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tipologia': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'nominati.incarico': {
            'Meta': {'object_name': 'Incarico', 'db_table': "u'incarico'"},
            'altri_compensi': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'compenso_anno': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'compenso_carica': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'data_fine': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'data_inizio': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'ente_cf': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nominati.Ente']", 'null': 'True', 'db_column': "'ente_cf'", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indennita_risultato': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'istituzione_cf': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nominati.Istituzione']", 'db_column': "'istituzione_cf'"}),
            'persona': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nominati.Persona']"}),
            'tipo_carica': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nominati.TipoCarica']"})
        },
        'nominati.istituzione': {
            'Meta': {'object_name': 'Istituzione', 'db_table': "u'istituzione'"},
            'codice_fiscale': ('django.db.models.fields.CharField', [], {'max_length': '11', 'primary_key': 'True'}),
            'comparto': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nominati.Comparto']"}),
            'denominazione': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'regione': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nominati.Regione']"})
        },
        'nominati.istituzionehasente': {
            'Meta': {'object_name': 'IstituzioneHasEnte', 'db_table': "u'istituzione_has_ente'"},
            'anno': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'dichiarazione_inviata': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'ente_cf': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nominati.Ente']", 'db_column': "'ente_cf'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'istituzione_cf': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nominati.Istituzione']", 'db_column': "'istituzione_cf'"}),
            'onere_complessivo': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'percentuale_partecipazione': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'nominati.persona': {
            'Meta': {'object_name': 'Persona', 'db_table': "u'persona'"},
            'cognome': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'data_nascita': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sesso': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'nominati.regione': {
            'Meta': {'object_name': 'Regione', 'db_table': "u'regione'"},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'nominati.tipocarica': {
            'Meta': {'object_name': 'TipoCarica', 'db_table': "u'tipo_carica'"},
            'denominazione': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'descrizione': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['nominati']