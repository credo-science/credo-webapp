# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return "Team %s" % self.name


class User(AbstractUser):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True)
    display_name = models.CharField(max_length=24)
    key = models.CharField(max_length=255, unique=True, blank=False)
    email = models.EmailField(unique=True, blank=False)
    email_confirmation_token = models.CharField(max_length=255, blank=True)
    language = models.CharField(max_length=10, default='en')  # ISO 639-1

    def __str__(self):
        return "User %s (%s)" % (self.display_name, self.email)

    def get_full_name(self):
        return self.display_name


# TODO: do we need this?
class Device(models.Model):
    device_id = models.CharField(max_length=255)
    device_model = models.CharField(max_length=255)
    system_version = models.CharField(max_length=255)
    type = models.CharField(max_length=255, default='phone_android')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "Device %s (%s)" % (self.device_id, self.device_model)


class Detection(models.Model):
    accuracy = models.FloatField()
    altitude = models.FloatField()
    frame_content = models.BinaryField(blank=True)
    height = models.IntegerField()
    width = models.IntegerField()
    d_id = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    provider = models.CharField(max_length=24)
    timestamp = models.BigIntegerField(db_index=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return "Detection %s" % self.id


class Ping(models.Model):
    timestamp = models.BigIntegerField(db_index=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "Ping %s" % self.id
