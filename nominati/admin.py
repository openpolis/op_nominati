from django.contrib import admin
from nominati.utils import ImproveRawIdFieldsForm
from nominati.models import *


class IstituzioneHasEnteInline(ImproveRawIdFieldsForm):
    model = IstituzioneHasEnte
    raw_id_fields = ('istituzione_cf', 'ente_cf', )
    extra = 1

class BilancioInline(admin.TabularInline):
    model = Bilancio
    extra = 1

class IncaricoInline(ImproveRawIdFieldsForm):
    raw_id_fields = ('istituzione_cf', 'ente_cf', 'persona')
    model = Incarico
    extra = 1

class IstituzioneAdmin(admin.ModelAdmin):
    inlines = (IstituzioneHasEnteInline,)
    search_fields = ['denominazione', '^codice_fiscale']

class EnteAdmin(admin.ModelAdmin):
    inlines = (BilancioInline, IstituzioneHasEnteInline, IncaricoInline )
    search_fields = ['denominazione', '^codice_fiscale']
    list_filter = ('tipologia_ente',)

class PersonaAdmin(admin.ModelAdmin):
    inlines = (IncaricoInline,)
    search_fields = ['^nome', '^cognome']

admin.site.register(Comparto)
admin.site.register(Regione)
admin.site.register(TipologiaEnte)
admin.site.register(Istituzione, IstituzioneAdmin)
admin.site.register(Ente, EnteAdmin)
admin.site.register(Persona, PersonaAdmin)
