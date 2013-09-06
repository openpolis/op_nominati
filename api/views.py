from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from api.serializers import EnteSerializer, PartecipazioneSerializer, ComposizionePartecipataSerializer, MultipleFieldLookupMixin,IncarichiSerializer
from nominati.models import Ente, Partecipazione, Partecipata, Incarico, Persona


@api_view(('GET',))
def api_root(request, format=None):
    """
    This is the root of NOMINATI API
    """

    return Response({
        'enti': reverse('api-enti', request=request, format=format),
        'partecipazioni': reverse('api-partecipazioni', request=request, format=format),
        'composizione-partecipata': reverse('api-composizione-partecipata', request=request, format=format),
        'incarichi': reverse('api-incarichi', request=request, format=format),
    })

class EntiList(generics.ListAPIView):
    """
    API endpoint that allows Ente to be viewed

    Parameters:
    qterm = string being present in the denominazione of the Ente
    [format=json]
    """
    queryset = Ente.objects.all()[:10]
    serializer_class = EnteSerializer
    paginate_by = 0


    def get_queryset(self):
        if 'qterm' in self.request.GET:
            qterm = self.request.GET['qterm']
            return Ente.objects.filter(denominazione__icontains=qterm).order_by('denominazione')
        else:
            return Ente.objects.all().order_by('denominazione')[:10]


class ComposizionePartecipataList(MultipleFieldLookupMixin,generics.ListAPIView):
    """
    API endpoint that allows the composition of a Partecipata to be viewed

    Parameters:
    anno=year
    cf=partecipata codice fiscale
    [format=json]
    """
    queryset = Partecipata.objects.all()[0].partecipazione_set.order_by('ente_cf__denominazione')

    serializer_class = ComposizionePartecipataSerializer
    paginate_by = 0
    lookup_fields = ('cf','anno')

    def get_queryset(self):
        if 'cf' in self.request.GET and 'anno' in self.request.GET:
            cf = self.request.GET['cf']
            anno = self.request.GET['anno']
            try:
                partecipata = Partecipata.objects.get(codice_fiscale = cf )
            except ObjectDoesNotExist:
                return self.queryset

            return partecipata.partecipazione_set.filter(anno=anno).order_by('ente_cf__denominazione')
        else:
            return self.queryset


class PartecipazioniList(generics.ListAPIView):
    """
    API endpoint that allows Partecipazioni to be viewed

    Parameters:
    anno = year
    istat = istat code of a comune
    complete = 0 or 1. If '1': displays all the partecipate, otherwise it excludes the partecipate with
     percentage of partecipazione == 0
    [format=json]
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





class IncarichiList(generics.ListAPIView):
    """
    API endpoint that allows Incarichi to be viewed

    Parameters:
    op_id = id openpolis of persona

    [format=json]
    """
    queryset = Incarico.objects.all()[:10]
    serializer_class = IncarichiSerializer
    paginate_by = 0

    def get_queryset(self):
        if 'op_id' in self.request.GET:
            op_id = self.request.GET['op_id']
            try:
                persona =  Persona.objects.get(openpolis_id=op_id)
            except ObjectDoesNotExist:
                return self.queryset

            return persona.incarico_set.all().order_by('-data_inizio')


        else:
            return self.queryset


