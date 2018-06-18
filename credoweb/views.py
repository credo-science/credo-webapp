# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
from collections import Counter
from datetime import datetime
import time

from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.cache import cache

from credocommon.exceptions import RegistrationException
from credocommon.helpers import register_user
from credocommon.models import Team, User, Detection

from credoweb.forms import RegistrationForm
from credoweb.helpers import get_global_stats, get_recent_detections, get_top_users, get_recent_users,\
    get_user_detections_page, format_date


def index(request):
    context = {
        'global_stats': get_global_stats(),
        'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        'recent_detections': get_recent_detections,
        'top_users': get_top_users,
        'recent_users': get_recent_users
    }
    return render(request, 'credoweb/index.html', context)


def detection_list(request, page=1):
    page = int(page)
    context = cache.get('detection_list_{}'.format(page))
    if not context:
        p = Paginator(
            Detection.objects.order_by('-timestamp').filter(visible=True).select_related('user', 'team'), 20).page(page)
        context = {
            'has_next': p.has_next(),
            'has_previous': p.has_previous(),
            'page_number': page,
            'detections': [{
                'date': format_date(d.timestamp),
                'timestamp': d.timestamp,
                'user': {
                    'name': d.user.username,
                    'display_name': d.user.display_name,
                },
                'team': {
                    'name': d.team.name,
                },
                'img': base64.encodestring(d.frame_content)
            } for d in p.object_list],
        }
        cache.set('detection_list_{}'.format(page), context)
    return render(request, 'credoweb/detection_list.html', context)


def user_list(request, page=1):
    page = int(page)
    context = cache.get('user_list_{}'.format(page))
    if not context:
        p = Paginator(
            User.objects.filter(detection__visible=True).annotate(detection_count=Count('detection')).order_by(
                '-detection_count'), 20).page(page)
        context = {
            'has_next': p.has_next(),
            'has_previous': p.has_previous(),
            'page_number': page,
            'users': [{
                'name': u.username,
                'display_name': u.display_name,
                'detection_count': u.detection_count
            } for u in p.object_list],
        }
        cache.set('user_list_{}'.format(page), context)
    return render(request, 'credoweb/user_list.html', context)


def team_list(request, page=1):
    page = int(page)
    context = cache.get('team_list_{}'.format(page))
    if not context:
        p = Paginator(Team.objects.filter(detection__visible=True).annotate(detection_count=Count('detection')).exclude(
            name__isnull=True).exclude(name__exact='').order_by('-detection_count'), 20).page(page)
        context = {
            'has_next': p.has_next(),
            'has_previous': p.has_previous(),
            'page_number': page,
            'teams': [{
                'name': t.name,
                'user_count': t.user_set.count(),
                'detection_count': t.detection_count,
            } for t in p.object_list],
        }
        cache.set('team_list_{}'.format(page), context)
    return render(request, 'credoweb/team_list.html', context)


def user_page(request, username='', page=1):
    page = int(page)
    u = get_object_or_404(User, username=username)
    user_detections_page = get_user_detections_page(u, page)
    user_detection_count = Detection.objects.filter(visible=True).filter(user=u).count()
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
    }
    return render(request, 'credoweb/user.html', context)


def team_page(request, name=''):
    t = get_object_or_404(Team, name=name)
    team_users = t.user_set.filter(detection__visible=True).annotate(detection_count=Count('detection'))
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


def register(request):
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        cd = form.cleaned_data
        try:
            register_user(cd['email'], cd['password'], cd['username'], cd['display_name'], cd['team'])
        except RegistrationException as e:
            return render(request, 'credoweb/register.html', {'form': form, 'message': e.message})
        return render(request, 'credoweb/register_complete.html')
    return render(request, 'credoweb/register.html', {'form': form})


def contest(request):
    time_start = datetime.now()
    start = datetime.strptime(request.GET['start'], '%Y-%m-%dT%H:%M')
    time_start = time_start.replace(year=start.year, month=start.month, day=start.day,
                                    hour=start.hour, minute=start.minute, second=0, microsecond=0)
    start = (time.mktime(time_start.timetuple())) * 1000
    duration = int(request.GET['duration']) * 60 * 1000  # From minutes to milliseconds
    max_brightness = float(request.GET['max_brightness'])

    tc = Counter()
    uc = Counter()

    recent_detections = []

    for d in Detection.objects.order_by('-timestamp').filter(visible=True).filter(brightness__lte=max_brightness)\
            .filter(timestamp__gt=start)\
            .filter(timestamp__lt=(start + duration)).select_related('user', 'team'):
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

    context = {
        'recent_detections': recent_detections[:int(request.GET['limit'])],
        'top_users': top_users,
        'top_teams': top_teams
    }
    return render(request, 'credoweb/contest.html', context)
