# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import time

from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.cache import cache
from django.db.models import Count
from django.http import HttpResponseNotFound, Http404
from django.shortcuts import render, get_object_or_404, redirect

from credocommon.exceptions import RegistrationException
from credocommon.helpers import register_user, generate_token
from credocommon.jobs import calculate_contest_results
from credocommon.models import Team, User, Detection

from credoweb.forms import RegistrationForm, ContestCreationForm
from credoweb.helpers import get_global_stats, get_recent_detections, get_top_users, get_recent_users, \
    get_user_detections_page, format_date, get_user_on_time_and_rank, get_user_detection_count_and_rank, \
    get_user_list_page, get_team_list_page


def index(request):
    context = {
        'global_stats': get_global_stats(),
        'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        'recent_detections': get_recent_detections,
        'top_users': get_top_users,
        'recent_users': get_recent_users
    }
    return render(request, 'credoweb/index.html', context)


def faq(request):
    context = {}
    return render(request, 'credoweb/faq.html', context)


def detection_list(request, page=1):
    try:
        page = int(page)
    except ValueError:
        raise Http404('Page index must be a number')

    context = cache.get('detection_list_{}'.format(page))

    if not context:
        try:
            p = Paginator(
                Detection.objects.order_by('-timestamp').filter(visible=True)
                                 .only('timestamp', 'frame_content', 'x', 'y', 'user', 'team'), 20).page(page)
        except EmptyPage:
            raise Http404('Detection list page not found')

        context = {
            'has_next': p.has_next(),
            'has_previous': p.has_previous(),
            'page_number': page,
            'detections': [{
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
                'img': base64.encodestring(d.frame_content)
            } for d in p.object_list],
        }
        cache.set('detection_list_{}'.format(page), context)
    return render(request, 'credoweb/detection_list.html', context)


def user_list(request, page=1):
    try:
        page = int(page)
    except ValueError:
        raise Http404('Page index must be a number')
    return render(request, 'credoweb/user_list.html', get_user_list_page(page))


def team_list(request, page=1):
    try:
        page = int(page)
    except ValueError:
        raise Http404('Page index must be a number')
    return render(request, 'credoweb/team_list.html', get_team_list_page(page))


def user_page(request, username='', page=1):
    try:
        page = int(page)
    except ValueError:
        raise Http404('Page index must be a number')
    u = get_object_or_404(User, username=username)

    try:
        user_detections_page = get_user_detections_page(u, page)
    except EmptyPage:
        raise Http404('User detection page not found')

    detection_count, detection_count_rank = get_user_detection_count_and_rank(u)

    on_time, on_time_rank = get_user_on_time_and_rank(u)
    context = {
        'user': {
            'name': u.username,
            'display_name': u.display_name,
            'on_time': on_time,
            'on_time_rank': on_time_rank,
            'team': {
                'name': u.team.name,
            },
            'detection_count': detection_count,
            'detection_count_rank': detection_count_rank
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


@staff_member_required
def contest_create(request):
    form = ContestCreationForm(request.POST or None)
    if form.is_valid():
        cd = form.cleaned_data
        contest_id = generate_token()[:8]

        filter_parameters = {
            'avbrightness_max': cd['avbrightness_max'],
            'maxbrightness_min': cd['maxbrightness_min'],
        }

        start_time = cd['start_time']

        start_time = start_time.replace(year=start_time.year, month=start_time.month, day=start_time.day,
                                        hour=start_time.hour, minute=start_time.minute, second=0, microsecond=0)
        start_timestamp = (time.mktime(start_time.timetuple())) * 1000

        duration = cd['duration'] * 3600 * 1000  # Hours -> milliseconds

        id_blacklist = [u.id for u in User.objects.filter(username__in=[n.strip() for n in cd['blacklist'].split(',')])]

        calculate_contest_results\
            .delay(contest_id, cd['name'], cd['description'],
                   start_timestamp, duration, cd['limit'], id_blacklist, filter_parameters)

        return redirect('contest_view', contest_id=contest_id)
    return render(request, 'credoweb/contest_create.html', {'form': form})


def contest_view(request, contest_id):
    context = cache.get('contest_{}'.format(contest_id))

    if not context:
        return HttpResponseNotFound('<h1>Contest results expired or not yet ready.</h1>')

    context['contest_id'] = contest_id

    return render(request, 'credoweb/contest.html', context)

