# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from credocommon.jobs import recalculate_user_stats
from credocommon.models import User


class Command(BaseCommand):
    help = 'Recalculate stats for all users'

    def handle(self, *args, **options):
        self.stdout.write("Creating jobs to recalculate user statistics...")

        for u in User.objects.all():
            recalculate_user_stats.delay(u.id)

        self.stdout.write("Done!")
