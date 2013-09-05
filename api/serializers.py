from rest_framework import serializers
from nominati.models import Ente, Partecipazione


class EnteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ente
        fields = ('denominazione','codice_fiscale')


class PartecipazioneSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Partecipazione
        fields = ('anno',)
