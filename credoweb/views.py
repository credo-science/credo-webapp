# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import time

from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.cache import cache

from credocommon.models import Team, User, Detection
from credoweb.helpers import get_global_stats, get_recent_detections, get_top_users, get_recent_users,\
    get_user_detections_page



def index(request):
    context = {
        'global_stats': get_global_stats(),
        'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        'recent_detections': get_recent_detections,
        'top_users': get_top_users,
        'recent_users': get_recent_users
    }
    return render(request, 'credoweb/index.html', context)

def user_list(request, page=1):
    page = int(page)
    context = cache.get('user_list_{}'.format(page))
    if not context:
        p = Paginator(User.objects.annotate(detection_count=Count('detection')).order_by('-detection_count'), 20).page(
            page)
        context = {
            'has_next': p.has_next(),
            'has_previous': p.has_previous(),
            'page_next': page + 1,
            'page_previous': page - 1,
            'page_number': page,
            'users': [{
                'name': u.username,
                'display_name': u.display_name,
                'detection_count': u.detection_count
            } for u in p.object_list],
        }
        cache.set('user_list_{}'.format(page), context)
    return render(request, 'credoweb/user_list.html', context)

def user_page(request, username='', page=1):
    page = int(page)
    u = get_object_or_404(User, username=username)
    user_detections_page = get_user_detections_page(u, page)
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
        'user_detections_page':  user_detections_page,
        'page_next': page + 1,
        'page_previous': page - 1,
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
