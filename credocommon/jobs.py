# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.cache import cache
from django.core.management import call_command
from django.db.models import Sum

from django_redis import get_redis_connection
from django_rq import job

from credocommon.helpers import validate_image
from credocommon.models import User, Ping, Detection


@job('data_export')
def data_export(id, since, until, limit, type):
    call_command('s3_data_export', id=id, since=since, until=until, limit=limit, type=type)


@job('low', result_ttl=3600)
def recalculate_on_time(user_id):
    u = User.objects.get(id=user_id)
    on_time = Ping.objects.filter(user=u).aggregate(Sum('on_time'))['on_time__sum']
    if on_time:
        get_redis_connection().zadd(cache.make_key('on_time'), on_time, user_id)


@job('low', result_ttl=3600)
def relabel_detections(start_id, limit):
    detections = Detection.objects.all()[start_id:start_id + limit]
    for d in detections:
        s = True

        if d.source != 'api_v2' or not d.frame_content:
            s = False

        if s and not validate_image(d.frame_content):
            s = False

        if s != d.visible:
            d.visible = s
            d.save()
