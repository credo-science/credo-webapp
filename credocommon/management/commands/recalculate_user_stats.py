# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from credocommon.jobs import recalculate_user_stats
from credocommon.models import User


class Command(BaseCommand):
    help = 'Recalculate on time for all users'

    def handle(self, *args, **options):
        users = User.objects.all()

        for u in users:
            recalculate_user_stats.delay(u.id)

        self.stdout.write("Done!")
