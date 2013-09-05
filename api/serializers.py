from rest_framework import serializers
from nominati.models import Ente


class EnteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ente
        fields = ('denominazione','codice_fiscale')


