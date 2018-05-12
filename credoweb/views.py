# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import time

from django.db.models import Count
from django.shortcuts import render, get_object_or_404

from credocommon.models import Team, User, Detection
from credoweb.helpers import get_global_stats, get_recent_detections, get_top_users, get_recent_users


def index(request):
    context = {
        'global_stats': get_global_stats(),
        'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        'recent_detections': get_recent_detections,
        'top_users': get_top_users,
        'recent_users': get_recent_users
    }
    return render(request, 'credoweb/index.html', context)


def user_page(request, username=''):
    u = get_object_or_404(User, username=username)
    user_recent_detections = Detection.objects.filter(user=u).order_by('-timestamp').filter(visible=True)[:20]
    user_detection_count = Detection.objects.filter(user=u).count()
    context = {
        'user': {
            'name': u.username,
            'display_name': u.display_name,
            'team': {
                'name': u.team.name,
            },
            'detection_count': user_detection_count
        },
        'user_recent_detections': [{
            'date': time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(d.timestamp/1000)),
            'img': base64.encodestring(d.frame_content)
        } for d in user_recent_detections]

    }
    return render(request, 'credoweb/user.html', context)


def team_page(request, name=''):
    t = get_object_or_404(Team, name=name)
    team_users = User.objects.filter(team=t).annotate(detection_count=Count('detection'))
    team_user_count = team_users.count()
    context = {
        'team': {
            'name': t.name,
            'user_count': team_user_count
        },
        'team_users': [{
            'name': u.username,
            'display_name': u.display_name,
            'detection_count': u.detection_count
        } for u in team_users]

    }
    return render(request, 'credoweb/team.html', context)


def confirm_email(request, token=''):
    u = get_object_or_404(User, email_confirmation_token=token)
    u.is_active = True
    u.save()
    context = {}
    return render(request, 'credoweb/confirm_email.html', context)
