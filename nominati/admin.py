import string
from django.contrib import admin
from nominati.filters import HasOpenpolisIdListFilter, HasBirthDateListFilter, HasBirthLocationListFilter
from nominati.utils.adminutils import ImproveRawIdFieldsTabularInlineForm, ImproveRawIdFieldsStackedInlineForm
from nominati.models import *
from nominati.utils.adminutils import get_json_response
from django.conf import settings
from django.template import loader, Context
from datetime import datetime
import re
from django.utils.http import urlencode



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

    change_list_template = "admin/nominati/Persona/change_list.html"
    inlines = (IncaricoInline,)
    list_per_page = 10
    search_fields = ['^nome', '^cognome']
    list_filter = ('openpolis_n_similars', HasOpenpolisIdListFilter, HasBirthDateListFilter, HasBirthLocationListFilter)
    list_display = ('__unicode__', 'data_nascita_it','luogo_nascita','persona_incarichi', 'openpolis_id', 'similars_merge')

    def data_nascita_it(self, obj):
        return '{0}/{1}/{2}'.format(obj.data_nascita.day, obj.data_nascita.month, obj.data_nascita.year)

    data_nascita_it.short_description = "Data nasc"

    def persona_incarichi(self,obj):
        incarichi = obj.incarichi

        temp = []
        for i in incarichi:
            singolo_incarico = {'ente_nominante':i.ente_nominante_cf, 'partecipata': i.partecipata_cf}
            temp.append(singolo_incarico)

        t = loader.get_template('admin/nominati/Persona/incarichi_table.html')
        context_dict = {'lista':temp}
        c = Context(context_dict)
        return t.render(c)
    persona_incarichi.allow_tags = True

    persona_incarichi.short_description = "Elenco Incarichi"

    def similars_merge(self, obj):

        diz_encode = {'first_name': obj.nome, 'last_name': obj.cognome}

        if obj.data_nascita:
            diz_date = {'birth_date': obj.data_nascita}
            diz_encode.update(diz_date)

        url = settings.OP_API_SIMILARITY_BASE_URL + "/?" + urlencode(diz_encode)
        json_resp = get_json_response(settings.OP_API_USER, settings.OP_API_PASS, url)

        if "error" in json_resp:
            return json_resp['error']

        #format date and charges string for template visualization
        for sim in json_resp:
            if sim['birth_date'] is not None and sim['birth_date'] !='':
                date = datetime.strptime(sim['birth_date'],"%Y-%m-%dT%H:%M:%S")
                sim['birth_date'] = '{0}/{1}/{2}'.format(date.day, date.month, date.year)
                sim['birth_date_eng'] = '{0}-{1}-{2}'.format(date.year, date.month, date.day)

            for i in range(0,len(sim['charges'])):
                sim['charges'][i] = re.sub('(\sal[\s]*\d\d/\d\d/\d\d\d\d)\s(.*)','\\1 <br/> \\2',sim['charges'][i])

        t = loader.get_template('admin/nominati/Persona/duplicati_table.html')

        #construct the context dict based on Persona's data then pass it to the template
        context_dict = { 'json_resp': json_resp ,'persona_id':obj.pk}
        if obj.op_id is not None:
            openpolis_id = {'openpolis_id': obj.op_id}
            context_dict.update(openpolis_id)
        if obj.data_nascita is not None:
            data_nascita = {'data_nascita': self.data_nascita_it(obj)}
            context_dict.update(data_nascita)
        if obj.luogo_nascita is not None:
            luogo_nascita = {'luogo_nascita': string.strip(obj.luogo_nascita)}
            context_dict.update(luogo_nascita)

        c = Context(context_dict)
        return t.render(c)


    similars_merge.allow_tags = True

admin.site.register(Comparto)
admin.site.register(Regione)
admin.site.register(TipologiaPartecipata)
admin.site.register(CompetenzaPartecipata)
admin.site.register(FinalitaPartecipata)
admin.site.register(Ente, EnteAdmin)
admin.site.register(Partecipata, PartecipataAdmin)
admin.site.register(Persona, PersonaAdmin)
admin.site.register(TipoCarica)

