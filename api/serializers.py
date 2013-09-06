from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse
from nominati.models import Ente, Partecipazione, Partecipata, Regione

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



class CustomComposizioneField(serializers.HyperlinkedRelatedField):

    read_only = True

    def get_url(self, obj, view_name, request, format):

        kwargs = {'anno': request.GET['anno'], 'cf': obj.codice_fiscale}
        return reverse(view_name, kwargs=kwargs, request=request, format=format)


    def get_object(self, queryset, view_name, view_args, view_kwargs):
        anno = view_kwargs['anno']
        cf = view_kwargs['codice_fiscale']

        return queryset.get(anno=anno, cf=cf)



class PartecipataSerializer(serializers.ModelSerializer):

    regione = RegioneSerializer(many=False)
    partecipata_da = CustomComposizioneField(view_name='api-composizione-partecipata')

    class Meta:
        model = Partecipata
        fields = (
            'codice_fiscale','denominazione','indirizzo', 'comune', 'cap',
            'provincia', 'regione','macro_tipologia','url', 'partecipata_da'
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