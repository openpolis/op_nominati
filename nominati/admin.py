from django.contrib import admin
from nominati.utils import ImproveRawIdFieldsTabularInlineForm, ImproveRawIdFieldsStackedInlineForm
from nominati.models import *


class PartecipazioneInline(ImproveRawIdFieldsTabularInlineForm):
    model = Partecipazione
    raw_id_fields = ('ente_cf', 'partecipata_cf', )
    extra = 1

class BilancioInline(admin.TabularInline):
    model = Bilancio
    extra = 1

class IncaricoInline(ImproveRawIdFieldsStackedInlineForm):
    raw_id_fields = ('ente_nominante_cf', 'partecipata_cf', 'persona')
    model = Incarico
    template = 'admin/nominati/Incarico/edit_inline/stacked.html'
    extra = 1


class EnteAdmin(admin.ModelAdmin):
    inlines = (PartecipazioneInline,)
    search_fields = ['denominazione', '^codice_fiscale']
    list_filter = ('comparto',)

class PartecipataAdmin(admin.ModelAdmin):
    inlines = (BilancioInline, PartecipazioneInline, IncaricoInline )
    search_fields = ['denominazione', '^codice_fiscale']
    list_filter = ('tipologia_partecipata', 'competenza_partecipata')

class PersonaAdmin(admin.ModelAdmin):
    inlines = (IncaricoInline,)
    search_fields = ['^nome', '^cognome']

admin.site.register(Comparto)
admin.site.register(Regione)
admin.site.register(TipologiaPartecipata)
admin.site.register(CompetenzaPartecipata)
admin.site.register(Ente, EnteAdmin)
admin.site.register(Partecipata, PartecipataAdmin)
admin.site.register(Persona, PersonaAdmin)
admin.site.register(TipoCarica)
