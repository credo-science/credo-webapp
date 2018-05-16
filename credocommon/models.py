# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time

from django.contrib.auth.models import AbstractUser
from django.db import models

from credocommon.helpers import generate_token


# Create your models here.
def get_default_team():
    return Team.objects.get_or_create(name='')[0]


class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return "Team %s" % self.name


class User(AbstractUser):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=50)
    key = models.CharField(max_length=255, db_index=True, unique=True, blank=False, default=generate_token)
    email = models.EmailField(unique=True, blank=False)
    email_confirmation_token = models.CharField(max_length=255, blank=True)
    language = models.CharField(max_length=10, default='en')  # ISO 639-1

    def __str__(self):
        return "User %s (%s)" % (self.display_name, self.email)

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.username
        if self.team_id is None:
            self.team = get_default_team()
        super(User, self).save(*args, **kwargs)

    def get_full_name(self):
        return self.display_name


class Device(models.Model):
    device_id = models.CharField(max_length=255)
    device_type = models.CharField(max_length=255, default='phone_android')
    device_model = models.CharField(max_length=255)
    system_version = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "Device %s (%s)" % (self.device_id, self.device_model)


class Detection(models.Model):
    accuracy = models.FloatField()
    altitude = models.FloatField()
    frame_content = models.BinaryField(blank=True, null=True)
    height = models.IntegerField()
    width = models.IntegerField()
    d_id = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    provider = models.CharField(max_length=24)
    timestamp = models.BigIntegerField(db_index=True)
    time_received = models.BigIntegerField(blank=False)
    source = models.CharField(max_length=50, blank=False, default='unspecified')
    visible = models.BooleanField(default=True, db_index=True
                                  )
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return "Detection %s" % self.id

    def save(self, *args, **kwargs):
        self.time_received = int(time.time() * 1000)
        super(Detection, self).save(*args, **kwargs)


class Ping(models.Model):
    timestamp = models.BigIntegerField(db_index=True)
    delta_time = models.IntegerField(blank=True, null=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "Ping %s" % self.id
