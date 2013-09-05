from rest_framework import viewsets, generics
from api.serializers import EnteSerializer
from nominati.models import Ente


class EntiList(generics.ListAPIView):
    """
    API endpoint that allows Ente to be viewed
    """
    queryset = Ente.objects.all()[:90]
    serializer_class = EnteSerializer
    paginate_by = 10

