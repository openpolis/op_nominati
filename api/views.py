from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from api.serializers import EnteSerializer, PartecipazioneSerializer, ComposizionePartecipataSerializer
from nominati.models import Ente, Partecipazione, Partecipata

@api_view(('GET',))
def api_root(request, format=None):
    """
    This is the root of NOMINATI API
    """

    return Response({
        'enti': reverse('api-enti', request=request, format=format),
        'partecipazioni': reverse('api-partecipazioni', request=request, format=format),
    })

class EntiList(generics.ListAPIView):
    """
    API endpoint that allows Ente to be viewed
    """
    queryset = Ente.objects.all()[:90]
    serializer_class = EnteSerializer
    paginate_by = 0


    def get_queryset(self):
        if 'qterm' in self.request.GET:
            qterm = self.request.GET['qterm']
            return Ente.objects.filter(denominazione__icontains=qterm)
        else:
            return Ente.objects.all()


class ComposizionePartecipataList(generics.ListAPIView):
    """
    API endpoint that allows the composition of a Partecipata to be viewed
    """
    queryset = Partecipata.objects.all()[0].partecipazione_set.all()
    serializer_class = ComposizionePartecipataSerializer
    paginate_by = 0

    def get_queryset(self):
        if 'cf' in self.request.GET and 'anno' in self.request.GET:
            cf = self.request.GET['cf']
            anno = self.request.GET['anno']
            try:
                partecipata = Partecipata.objects.get(codice_fiscale = cf )
            except ObjectDoesNotExist:
                return self.queryset

            return partecipata.partecipazione_set.filter(anno=anno).order_by('ente_cf__denominazione')


class PartecipazioniList(generics.ListAPIView):
    """
    API endpoint that allows Partecipazioni to be viewed
    """
    queryset = Partecipazione.objects.all().order_by('partecipata_cf__denominazione')[:10]
    serializer_class = PartecipazioneSerializer
    paginate_by = 0

    def get_queryset(self):
        if 'istat' in self.request.GET and \
            'anno' in self.request.GET and \
            'complete' in self.request.GET:

            istat = self.request.GET['istat']
            anno = self.request.GET['anno']
            # if the "complete" flag is true all the Partecipazioni are displayed
            # even those with 0% of partecipazione
            complete = self.request.GET['complete']

            if complete in ['1','0']:

                if complete == '1':
                    return Partecipazione.objects. \
                        filter(anno=anno, ente_cf__codice_istat=istat).\
                        order_by('partecipata_cf__denominazione')
                else:
                    return Partecipazione.objects. \
                        filter(anno=anno, ente_cf__codice_istat=istat, percentuale_partecipazione__gt = 0).\
                        order_by('partecipata_cf__denominazione')
            else:
                return self.queryset
        else:
            return self.queryset


