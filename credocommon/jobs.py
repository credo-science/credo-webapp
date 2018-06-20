# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.cache import cache
from django.core.management import call_command
from django.db.models import Sum

from django_rq import job

from credocommon.models import User, Ping


@job('data_export')
def data_export(id, since, until, limit, type):
    call_command('s3_data_export', id=id, since=since, until=until, limit=limit, type=type)


@job('low', result_ttl=3600)
def recalculate_on_time(user_id):
    u = User.objects.get(id=user_id)
    on_time = Ping.objects.filter(user=u).aggregate(Sum('on_time'))['on_time__sum']
    cache.set('on_time_{}'.format(u.id), on_time, timeout=3600 * 24 * 30)
