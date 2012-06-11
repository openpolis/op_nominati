from django.db.models import Q
from django.db.models.query import QuerySet

from datetime import datetime

class TimeFramedQuerySet(QuerySet):
    """
    A custom ``QuerySet`` allowing easy retrieval of current, past and future instances 
    of a timeframed model.
    
    Here, a *timeframed model* denotes a model class having an associated time range.
    
    We assume that the time range is described by two ``Date`` (or ``DateTime``) fields
    named ``data_inizio`` and ``data_fine``, respectively.
    """
    def past(self):
        """
        Return a QuerySet containing the *past* instances of the model
        (i.e. those having an end date which is in the past).
        """
        now = datetime.now()
        return self.filter(data_fine__lte=now)
    
    def future(self):
        """
        Return a QuerySet containing the *future* instances of the model
        (i.e. those having a start date which is in the future).
        """
        now = datetime.now()
        return self.filter(data_inizio__gte=now)

    def current(self, moment=None):
        """
        Return a QuerySet containing the *current* instances of the model
        at the given moment in time, if the parameter is spcified
        now if it is not
        @moment - is a datetime, expressed in the YYYY-MM-DD format
        (i.e. those for which the moment date-time lies within their associated time range).
        """
        if moment is None:
            moment = datetime.now()
        else:
            moment = datetime.strptime(moment, "%Y-%m-%d")

        return self.filter(Q(data_inizio__lte=moment) &
                           Q(data_fine__gte=moment) | Q(data_fine__isnull=True))