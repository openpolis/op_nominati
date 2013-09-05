from rest_framework import generics
from api.serializers import EnteSerializer, PartecipazioneSerializer
from nominati.models import Ente, Partecipazione


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


class PartecipazioniList(generics.ListAPIView):
    """
    API endpoint that allows Partecipazioni to be viewed
    """
    queryset = Partecipazione.objects.all()[:90]
    serializer_class = PartecipazioneSerializer
    paginate_by = 0



