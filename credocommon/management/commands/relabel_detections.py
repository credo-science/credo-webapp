# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from credocommon.jobs import relabel_detections
from credocommon.models import Detection


class Command(BaseCommand):
    help = 'Recalculate on time for all users'

    def handle(self, *args, **options):
        count = Detection.objects.latest('id')

        self.stdout.write('Relabeling {} detections'.format(count))

        for i in range(0, count, 1000):
            relabel_detections.delay(i, 1000)

        self.stdout.write("Done!")
