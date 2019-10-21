# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from credocommon.jobs import recalculate_team_stats
from credocommon.models import Team


class Command(BaseCommand):
    help = "Recalculate stats for all teams"

    def handle(self, *args, **options):
        self.stdout.write("Creating jobs to recalculate team statistics...")

        for t in Team.objects.all():
            recalculate_team_stats.delay(t.id)

        self.stdout.write("Done")
