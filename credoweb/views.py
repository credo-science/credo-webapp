# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse

from django.db.models import Count

from credoapi.models import Team, User, Device, Detection

import base64


def index(request):
    recent_detections = Detection.objects.all().order_by('-timestamp')[:20]
    top_users = User.objects.annotate(detection_count=Count('detection')).order_by('-detection_count')[:5]
    context = {
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
