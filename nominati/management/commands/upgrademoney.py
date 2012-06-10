# -*- coding: utf-8 -*-
from django.conf import settings
import logging
from django.core.management.base import BaseCommand

from nominati.models import Incarico


class Command(BaseCommand):
    """
    Task per aggiornare i compensi totali
    """
    help = "Aggiorna compensi totali per gli incarichi"

    logger = logging.getLogger('countsimilarity')

    def handle(self, *labels, **options):
        self.logger.info("Inizio script")

        for n, i in enumerate(Incarico.objects.all()):
            self.logger.info("%s: %s" % (n, i.tipo_carica.denominazione))
            i.compenso_totale = 0
            i.save()
            self.logger.info("nuovo compenso: %s" % i.compenso_totale)



