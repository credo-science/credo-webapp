# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from acra.models import CrashReport


@csrf_exempt
def report(request):
    if request.method != "POST":
        return HttpResponse(status=400)
    CrashReport.objects.create(data=request.body)
    return HttpResponse(status=200)
