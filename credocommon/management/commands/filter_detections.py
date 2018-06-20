# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from credocommon.models import Detection
from credocommon.helpers import validate_image, rate_brightness


class Command(BaseCommand):
    help = 'Validate detections'

    def handle(self, *args, **options):
        detections = Detection.objects.all()

        for d in detections:
            if d.frame_content:
                d.brightness = rate_brightness(d.frame_content)
                d.save()
            if (not d.frame_content) or validate_image(d.frame_content):
                self.stdout.write("Hiding detection %s (image validation failed)" % d.id)
                d.visible = False
                d.save()
            if abs(d.time_received - d.timestamp) > 3600 * 24 * 365 * 5 * 1000:
                self.stdout.write("Hiding detection %s (invalid date)" % d.id)
                d.visible = False
                d.save()

        self.stdout.write("Done!")
