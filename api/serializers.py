from rest_framework import serializers
from nominati.models import Ente, Partecipazione, Partecipata, Regione


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
        fields = ('denominazione','indirizzo', 'comune', 'cap', 'provincia', 'regione','macro_tipologia','url')


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