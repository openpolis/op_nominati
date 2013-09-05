from rest_framework import serializers
from nominati.models import Ente, Partecipazione, Partecipata


class EnteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ente
        fields = ('denominazione','codice_fiscale')


class PartecipataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partecipata
        fields = ('denominazione',)


class PartecipazioneSerializer(serializers.ModelSerializer):
    partecipata_cf = PartecipataSerializer(many=False)

    class Meta:
        model = Partecipazione
        fields = ('percentuale_partecipazione', 'partecipata_cf')
