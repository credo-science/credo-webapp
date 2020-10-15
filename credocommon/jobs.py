# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
from collections import Counter
import io
import os

from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command
from django.db.models import Sum, Min

from django_redis import get_redis_connection
from django_rq import job

from PIL import Image

from credocommon.helpers import (
    validate_image,
    get_average_brightness,
    get_max_brightness,
)
from credocommon.models import User, Team, Ping, Detection, Device
from credoweb.helpers import format_date, get_user_detections_page


@job("data_export")
def data_export(id, since, until, limit, type):
    call_command(
        "s3_data_export", id=id, since=since, until=until, limit=limit, type=type
    )


@job("data_export")
def mapping_export(job_id, mapping_type):
    import boto3
    import simplejson

    filename = "mapping_export_{}.json".format(job_id)

    if mapping_type == "device":
        data = {
            "devices": Device.objects.values(
                "id", "user_id", "device_type", "device_model", "system_version"
            )
        }
    elif mapping_type == "user":
        data = {"users": User.objects.values("id", "username", "display_name")}
    elif mapping_type == "team":
        data = {"teams": Team.objects.values("id", "name")}

    length = len(data)

    s3 = boto3.resource(
        "s3",
        aws_access_key_id=settings.S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        endpoint_url=settings.S3_ENDPOINT_URL,
    )

    with open(settings.EXPORT_TMP_FOLDER + filename, "w") as outfile:
        for chunk in simplejson.JSONEncoder(iterable_as_array=True).iterencode(data):
            outfile.write(chunk)

    bucket = s3.Bucket(settings.S3_BUCKET)

    bucket.upload_file(settings.EXPORT_TMP_FOLDER + filename, filename)

    os.remove(settings.EXPORT_TMP_FOLDER + filename)

    return length


@job("low", timeout=600, result_ttl=1200)
def recalculate_user_stats(user_id):
    if not cache.set(
        "user_stats_recently_recalculated_{}".format(user_id), 1, timeout=300, nx=True
    ):
        return "skipped"

    u = User.objects.get(id=user_id)

    on_time = Ping.objects.filter(user=u).aggregate(Sum("on_time"))["on_time__sum"]
    detection_count = Detection.objects.filter(user=u).filter(visible=True).count()

    r = get_redis_connection()

    if on_time:
        r.zadd(cache.make_key("on_time"), {user_id: on_time})

        if not r.zscore(cache.make_key("start_time"), user_id):
            start_time = (
                Ping.objects.filter(user=u)
                .filter(on_time__gt=0)
                .aggregate(Min("timestamp"))["timestamp__min"]
            )
            r.zadd(cache.make_key("start_time"), {user_id: start_time})

    r.zadd(cache.make_key("detection_count"), {user_id: detection_count})

    _ = get_user_detections_page(u, 1, preload=True)

    return on_time, detection_count


@job("low", timeout=600, result_ttl=1200)
def recalculate_team_stats(team_id):
    if not cache.set(
        "team_stats_recently_recalculated_{}".format(team_id), 1, timeout=300, nx=True
    ):
        return "skipped"

    t = Team.objects.get(id=team_id)

    if t.name:
        detection_count = Detection.objects.filter(team=t).filter(visible=True).count()

        r = get_redis_connection()
        r.zadd(cache.make_key("team_detection_count"), {team_id: detection_count})

        return detection_count

    else:
        cache.set(
            "team_stats_recently_recalculated_{}".format(team_id),
            1,
            timeout=3600 * 24 * 7,
        )

    return "ignored"


@job("low", timeout=600, result_ttl=1200)
def relabel_detections(start_id, limit):
    detections = Detection.objects.filter(id__gte=start_id).filter(
        id__lt=start_id + limit
    )
    r = get_redis_connection()

    for d in detections:
        s = True

        if d.source != "api_v2" or not d.frame_content:
            s = False

        if s and not validate_image(d.frame_content):
            s = False

        if s:
            start_time = r.zscore(cache.make_key("start_time"), d.user_id)
            if start_time:
                s = d.timestamp > start_time
            else:
                s = False

        if s != d.visible:
            d.visible = s
            d.save()


@job("default", result_ttl=3600 * 24 * 30)
def calculate_contest_results(
    contest_id,
    name,
    description,
    start,
    duration,
    limit,
    id_blacklist,
    filter_parameters,
):
    avbrightness_max = filter_parameters["avbrightness_max"]
    maxbrightness_min = filter_parameters["maxbrightness_min"]

    tc = Counter()
    uc = Counter()

    recent_detections = []

    for d in (
        Detection.objects.order_by("-timestamp")
        .filter(visible=True)
        .filter(timestamp__gt=start)
        .filter(timestamp__lt=(start + duration))
        .select_related("user", "team")
    ):

        if d.user.id in id_blacklist:
            continue

        try:
            img = Image.open(io.BytesIO(d.frame_content))
        except IOError:
            continue

        avb = get_average_brightness(img)
        mb = get_max_brightness(img)

        if avb > avbrightness_max or mb < maxbrightness_min:
            continue

        uc[(d.user.username, d.user.display_name)] += 1

        if d.team.name:
            tc[d.team.name] += 1

        recent_detections.append(
            {
                "date": format_date(d.timestamp),
                "x": d.x,
                "y": d.y,
                "user": {"name": d.user.username, "display_name": d.user.display_name},
                "team": {"name": d.team.name},
                "img": base64.encodestring(d.frame_content),
            }
        )

    top_users = uc.most_common(5)

    top_teams = tc.most_common(5)

    data = {
        "name": name,
        "description": description,
        "recent_detections": recent_detections[:limit],
        "top_users": top_users,
        "top_teams": top_teams,
    }

    cache.set("contest_{}".format(contest_id), data, timeout=3600 * 24 * 30)


@job("low", result_ttl=3600)
def hide_user_hot_pixel_detections(user_id):
    u = User.objects.get(id=user_id)
    r = get_redis_connection()

    pixels = set()

    for d in Detection.objects.filter(user=u, visible=True, x__isnull=False).only(
        "x", "y", "visible"
    ):
        if (d.x, d.y) not in pixels:
            pixels.add((d.x, d.y))
        else:
            d.visible = False
            d.save()

    r.delete(cache.make_key("pixels_{}".format(u.id)))

    if pixels:
        r.sadd(
            cache.make_key("pixels_{}".format(u.id)),
            *["{} {}".format(c[0], c[1]) for c in pixels]
        )

    return len(pixels)
