# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
from collections import Counter
import io

from django.core.cache import cache
from django.core.management import call_command
from django.db.models import Sum, Min

from django_redis import get_redis_connection
from django_rq import job

from PIL import Image

from credocommon.helpers import validate_image, get_average_brightness, get_max_brightness
from credocommon.models import User, Team, Ping, Detection
from credoweb.helpers import format_date


@job('data_export')
def data_export(id, since, until, limit, type):
    call_command('s3_data_export', id=id, since=since, until=until, limit=limit, type=type)


@job('low', result_ttl=3600)
def recalculate_user_stats(user_id):
    if not cache.set('user_stats_recently_recalculated_{}'.format(user_id), 1, timeout=10, nx=True):
        return 'skipped'

    u = User.objects.get(id=user_id)

    on_time = Ping.objects.filter(user=u).aggregate(Sum('on_time'))['on_time__sum']
    detection_count = Detection.objects.filter(user=u).filter(visible=True).count()

    r = get_redis_connection()

    if on_time:
        r.zadd(cache.make_key('on_time'), on_time, user_id)

        if not r.zscore(cache.make_key('start_time'), user_id):
            start_time = Ping.objects.filter(user=u).filter(on_time__gt=0)\
                                     .aggregate(Min('timestamp'))['timestamp__min']
            r.zadd(cache.make_key('start_time'), start_time, user_id)

    r.zadd(cache.make_key('detection_count'), detection_count, user_id)

    return on_time, detection_count


@job('low', result_ttl=3600)
def recalculate_team_stats(team_id):
    if not cache.set('team_stats_recently_recalculated_{}'.format(team_id), 1, timeout=10, nx=True):
        return 'skipped'

    t = Team.objects.get(id=team_id)

    if t.name:
        detection_count = Detection.objects.filter(team=t).filter(visible=True).count()

        r = get_redis_connection()
        r.zadd(cache.make_key('team_detection_count'), detection_count, team_id)

        return detection_count

    return 'ignored'


@job('low', result_ttl=3600)
def relabel_detections(start_id, limit):
    detections = Detection.objects.filter(id__gte=start_id).filter(id_lt=start_id + limit)
    for d in detections:
        s = True

        if d.source != 'api_v2' or not d.frame_content:
            s = False

        if s and not validate_image(d.frame_content):
            s = False

        if s != d.visible:
            d.visible = s
            d.save()


@job('default', result_ttl=3600*24*30)
def calculate_contest_results(contest_id, name, description, start, duration, limit, id_blacklist, filter_parameters):
    avbrightness_max = filter_parameters['avbrightness_max']
    maxbrightness_min = filter_parameters['maxbrightness_min']

    tc = Counter()
    uc = Counter()

    recent_detections = []

    for d in Detection.objects.order_by('-timestamp').filter(visible=True)\
            .filter(timestamp__gt=start)\
            .filter(timestamp__lt=(start + duration)).select_related('user', 'team'):

        if d.user.id in id_blacklist:
            continue

        try:
            img = Image.open(io.BytesIO(d.frame_content))
        except IOError:
            continue

        avb = get_average_brightness(img)
        mb = get_max_brightness(img)

        if avb > avbrightness_max or mb < maxbrightness_min:
            continue

        uc[(d.user.username, d.user.display_name)] += 1

        if d.team.name:
            tc[d.team.name] += 1

        recent_detections.append({
            'date': format_date(d.timestamp),
            'user': {
                'name': d.user.username,
                'display_name': d.user.display_name,
            },
            'team': {
                'name': d.team.name,
            },
            'img': base64.encodestring(d.frame_content)
        })

    top_users = uc.most_common(5)

    top_teams = tc.most_common(5)

    data = {
        'name': name,
        'description': description,
        'recent_detections': recent_detections[:limit],
        'top_users': top_users,
        'top_teams': top_teams
    }

    cache.set('contest_{}'.format(contest_id), data, timeout=3600*24*30)

