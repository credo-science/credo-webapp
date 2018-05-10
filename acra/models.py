# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time

from django.db import models


class CrashReport(models.Model):
    timestamp = models.BigIntegerField(blank=False)
    data = models.CharField(max_length=10000)

    def save(self, *args, **kwargs):
        self.time_received = int(time.time())
        super(CrashReport, self).save(*args, **kwargs)
