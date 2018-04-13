# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse

from django.db.models import Count

from credoapi.models import Team, User, Device, Detection

import base64


def index(request):
    recent_detections = Detection.objects.all().order_by('-timestamp')[:20]
    top_users = User.objects.annotate(detection_count=Count('detection')).order_by('-detection_count')[:5]
    context = {
        'detections_total': Detection.objects.count(),
        'users_total': User.objects.count(),
        'teams_total': Team.objects.count(),
        'recent_detections': [{
            'date': d.timestamp,
            'user': d.user.name,
            'team': d.user.team,
            'img': base64.encodestring(d.frame_content)
        } for d in recent_detections],
        'top_users': [{
            'name': u.name,
            'detection_count': u.detection_count
        } for u in top_users]
    }
    return render(request, 'credoweb/index.html', context)


def user(request, name=''):
    u = get_object_or_404(User, name=name)
    user_recent_detections = Detection.objects.filter(user=u).order_by('-timestamp')#[:20]
    user_detection_count = Detection.objects.filter(user=u).count()
    context = {
        'user': {
            'name': u.name,
            'team': u.team,
            'detection_count': user_detection_count
        },
        'user_recent_detections': [{
            'date': d.timestamp,
            'img': base64.encodestring(d.frame_content)
        } for d in user_recent_detections]

    }
    return render(request, 'credoweb/user.html', context)
