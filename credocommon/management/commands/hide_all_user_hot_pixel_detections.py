# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from credocommon.jobs import hide_user_hot_pixel_detections
from credocommon.models import User


class Command(BaseCommand):
    help = "Hides detections caused by hot pixels for all users"

    def handle(self, *args, **options):
        self.stdout.write("Creating jobs to hide hot pixel detections for each user...")

        for u in User.objects.all():
            hide_user_hot_pixel_detections.delay(u.id)

        self.stdout.write("Done!")
