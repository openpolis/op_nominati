# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Persona.sesso'
        db.alter_column(u'persona', 'sesso', self.gf('django.db.models.fields.IntegerField')())

    def backwards(self, orm):

        # Changing field 'Persona.sesso'
        db.alter_column(u'persona', 'sesso', self.gf('django.db.models.fields.CharField')(max_length=255))

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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sesso': ('django.db.models.fields.IntegerField', [], {'blank': 'True'})
        },
        'nominati.regione': {
            'Meta': {'object_name': 'Regione', 'db_table': "u'regione'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'nominati.tipocarica': {
            'Meta': {'object_name': 'TipoCarica', 'db_table': "u'tipo_carica'"},
            'denominazione': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'descrizione': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['nominati']