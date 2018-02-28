# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.

class Team(models.Model):
    name = models.CharField(max_length=255)


# TODO: integrate with Django's user?
class User(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    email = models.CharField(max_length=255)
    name = models.CharField(max_length=24)
    registerDate = models.DateTimeField()
    key = models.CharField(max_length=255)


# TODO: do we need this?
class Device(models.Model):
    deviceId = models.CharField(max_length=255)
    deviceModel = models.CharField(max_length=255)
    androidVersion = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Detection(models.Model):
    accuracy = models.FloatField()
    altitude = models.FloatField()
    frame_content = models.BinaryField()
    height = models.IntegerField()
    width = models.IntegerField()
    id = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    provider = models.CharField(max_length=24)
    timestamp = models.DateTimeField()
