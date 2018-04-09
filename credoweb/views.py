# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse

from credoapi.models import Team, User, Device, Detection


def index(request):
    context = {
        'detections_recent': Detection.objects.all().order_by('-timestamp')[:20]
    }
    return render(request, 'credoweb/index.html', context)
