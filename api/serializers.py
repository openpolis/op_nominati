from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse
from nominati.models import Ente, Partecipazione, Partecipata, Regione, Incarico, TipoCarica


class MultipleFieldLookupMixin(object):
    """
    Apply this mixin to any view or viewset to get multiple field filtering
    based on a `lookup_fields` attribute, instead of the default single field filtering.
    """
    def get_object(self):
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}
        for field in self.lookup_fields:
            filter[field] = self.kwargs[field]
        return get_object_or_404(queryset, **filter)  # Lookup the object


class EnteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ente
        fields = ('denominazione','codice_fiscale')

class RegioneSerializer(serializers.ModelSerializer):
    class Meta:
        model= Regione
        fields = ('denominazione',)


class PartecipataSerializer(serializers.ModelSerializer):

    regione = RegioneSerializer(many=False)

    class Meta:
        model = Partecipata
        fields = (
            'codice_fiscale','denominazione','indirizzo', 'comune', 'cap',
            'provincia', 'regione','macro_tipologia','url',
        )


class PartecipazioneSerializer(serializers.ModelSerializer):
    partecipata_cf = PartecipataSerializer(many=False)

    class Meta:
        model = Partecipazione
        fields = ('percentuale_partecipazione', 'partecipata_cf')


class ComposizionePartecipataSerializer(serializers.ModelSerializer):
    ente_cf = EnteSerializer(many=False)
    class Meta:
        model= Partecipazione
        fields = ('percentuale_partecipazione', 'ente_cf')

class TipoCaricaSerializer(serializers.ModelSerializer):
    class Meta:
        model=TipoCarica
        fields = ('denominazione',)


class IncarichiSerializer(serializers.ModelSerializer):
    ente_nominante_cf = EnteSerializer(many=False)
    tipo_carica = TipoCaricaSerializer(many=False)
    partecipata_cf = PartecipataSerializer(many=False)

    class Meta:
        model = Incarico
        fields = ('compenso_anno', 'compenso_carica','altri_compensi','compenso_totale','indennita_risultato',
            'tipo_carica','data_inizio', 'data_fine', 'ente_nominante_cf', 'partecipata_cf')