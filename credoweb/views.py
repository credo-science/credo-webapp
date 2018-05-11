# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404

from django.db.models import Count

from credocommon.models import Team, User, Detection

import base64


def index(request):
    recent_detections = Detection.objects.order_by('-timestamp').filter(visible=True).select_related('user', 'team')[:20]
    top_users = User.objects.annotate(detection_count=Count('detection')).order_by('-detection_count')[:5]
    recent_users = User.objects.annotate(detection_count=Count('detection')).order_by('-id')[:5]
    context = {
        'detections_total': Detection.objects.count(),
        'users_total': User.objects.count(),
        'teams_total': Team.objects.count(),
        'recent_detections': [{
            'date': d.timestamp,
            'user': {
                'name': d.user.username,
                'display_name': d.user.display_name,
            },
            'team': {
                'name': d.team.name,
            },
            'img': base64.encodestring(d.frame_content)
        } for d in recent_detections],
        'top_users': [{
            'name': u.username,
            'display_name': u.display_name,
            'detection_count': u.detection_count
        } for u in top_users],
        'recent_users': [{
            'name': u.username,
            'display_name': u.display_name,
            'detection_count': u.detection_count
        } for u in recent_users]
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
            'date': d.timestamp,
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
