# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Refresh all data stored in Redis. (recalculates user and team stats and relabels detections)'

    def handle(self, *args, **options):
        call_command('recalculate_user_stats')  # We want to have start_time data before we relabel detections
        call_command('relabel_detections')
        call_command('hide_all_user_hot_pixel_detections')
        call_command('recalculate_user_stats')
        call_command('recalculate_team_stats')
