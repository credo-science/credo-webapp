# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Detection, Device, Team, User, Ping

# Register your models here.

admin.site.register(Detection)
admin.site.register(Device)
admin.site.register(Team)
admin.site.register(User)
admin.site.register(Ping)
