# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import time

from django.core.cache import cache
from django.db.models import Count

from credocommon.models import Team, User, Detection


def get_global_stats():
    return cache.get_or_set('global_stats', lambda: {
        'detections_total': Detection.objects.count(),
        'users_total': User.objects.count(),
        'teams_total': Team.objects.count(),
    })


def get_recent_detections():
    return [{
            'date': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(d.timestamp/1000)),
            'user': {
                'name': d.user.username,
                'display_name': d.user.display_name,
            },
            'team': {
                'name': d.team.name,
            },
            'img': base64.encodestring(d.frame_content)
            } for d in Detection.objects.order_by('-timestamp').filter(visible=True).select_related('user', 'team')[:20]]


def get_top_users():
    return [{
            'name': u.username,
            'display_name': u.display_name,
            'detection_count': u.detection_count
            } for u in User.objects.annotate(detection_count=Count('detection')).order_by('-detection_count')[:5]]


def get_recent_users():
    return [{
            'name': u.username,
            'display_name': u.display_name,
            'detection_count': u.detection_count
            } for u in User.objects.annotate(detection_count=Count('detection')).order_by('-id')[:5]]
