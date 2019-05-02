# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import time

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Count

from django_redis import get_redis_connection

from credocommon.models import Team, User, Detection


def format_date(timestamp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000)) + ".{:03}".format(timestamp % 1000)


def get_global_stats():
    data = cache.get('global_stats')

    if not data:
        r = get_redis_connection(write=False)
        data = {
            'detections_total': Detection.objects.filter(visible=True).count(),
            'users_total': r.zcard(cache.make_key('start_time')),
            'teams_total': Team.objects.count(),
        }
        cache.set('global_stats', data)

    return data


def get_recent_detections():
    return [{
        'date': format_date(d.timestamp),
        'timestamp': d.timestamp,
        'x': d.x,
        'y': d.y,
        'user': {
            'name': d.user.username,
            'display_name': d.user.display_name,
        },
        'team': {
            'name': d.team.name,
        },
        'img': base64.encodebytes(d.frame_content).decode()
    } for d in Detection.objects.order_by('-timestamp').filter(visible=True)
                   .only('timestamp', 'frame_content', 'user', 'team')[:20]]


def get_top_users():
    top = get_redis_connection(write=False) \
        .zrevrange(cache.make_key('detection_count'), 0, 4, withscores=True)
    return [{
        'name': u.username,
        'display_name': u.display_name,
        'detection_count': int(top[i][1])
    } for i, u in enumerate([User.objects.get(id=id) for id in [t[0] for t in top]])]


def get_recent_users():
    return [{
        'name': u.username,
        'display_name': u.display_name,
        'detection_count': get_user_detection_count_and_rank(u)[0]
    } for u in User.objects.order_by('-id')[:5]]


def get_user_detections_page(user, page):
    data = cache.get('user_{}_recent_detections_{}'.format(user.id, page))
    if not data:
        p = Paginator(Detection.objects.filter(user=user).order_by('-timestamp').filter(visible=True), 20).page(page)
        data = {
            'has_next': p.has_next(),
            'has_previous': p.has_previous(),
            'page_number': page,
            'detections': [{
                'date': format_date(d.timestamp),
                'timestamp': d.timestamp,
                'img': base64.encodebytes(d.frame_content).decode(),
                'x': d.x,
                'y': d.y
            } for d in p.object_list]
        }
        cache.set('user_{}_recent_detections_{}'.format(user.id, page), data)
    return data


def get_user_list_page(page):
    data = cache.get('user_list_{}'.format(page))
    if not data:
        r = get_redis_connection(write=False)
        top = r.zrevrange(cache.make_key('detection_count'), 20 * (page - 1), 19 + 20 * (page - 1), withscores=True)
        top = [(int(t[0]), int(t[1])) for t in top if t[1]]  # Remove users with no detections
        users = {u.id: u for u in User.objects.filter(id__in=[t[0] for t in top])}

        data = {
            'has_next': len(top) == 20,
            'has_previous': page > 1,
            'page_number': page,
            'users': [{
                'name': users[t[0]].username,
                'display_name': users[t[0]].display_name,
                'detection_count': t[1]
            } for t in top],
        }
        cache.set('user_list_{}'.format(page), data)
    return data


def get_team_list_page(page):
    data = cache.get('team_list_{}'.format(page))
    if not data:
        r = get_redis_connection(write=False)
        top = r.zrevrange(cache.make_key('team_detection_count'), 20 * (page - 1), 19 + 20 * (page - 1),
                          withscores=True)
        top = [(int(t[0]), int(t[1])) for t in top if t[1]]  # Remove teams with no detections
        teams = {team.id: team for team in Team.objects.filter(id__in=[t[0] for t in top])
            .annotate(user_count=Count('user'))}

        data = {
            'has_next': len(top) == 20,
            'has_previous': page > 1,
            'page_number': page,
            'teams': [{
                'name': teams[t[0]].name,
                'user_count': teams[t[0]].user_count,
                'detection_count': t[1]
            } for t in top],
        }
        cache.set('team_list_{}'.format(page), data)
    return data


def get_user_on_time_and_rank(user):
    on_time = get_redis_connection(write=False).zscore(cache.make_key('on_time'), user.id)
    if not on_time:
        return 0, 'no '

    rank = get_redis_connection(write=False).zrevrank(cache.make_key('on_time'), user.id)

    hours, remainder = divmod(int(on_time) / 1000, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '{}h {}m'.format(int(hours), int(minutes)), rank + 1


def get_user_detection_count_and_rank(user):
    r = get_redis_connection(write=False)

    detection_count = r.zscore(cache.make_key('detection_count'), user.id)
    if not detection_count:
        return 0, 'no '

    rank = r.zrevrank(cache.make_key('detection_count'), user.id)

    return int(detection_count), rank + 1


def get_team_detection_count_and_rank(team):
    r = get_redis_connection(write=False)

    detection_count = r.zscore(cache.make_key('team_detection_count'), team.id)
    if not detection_count:
        return 0, 'no '

    rank = r.zrevrank(cache.make_key('detection_count'), team.id)

    return int(detection_count), rank + 1
