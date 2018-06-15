from __future__ import unicode_literals

from django.core.management import call_command

from django_rq import job


@job('data_export')
def data_export(id, since, until, limit, type):
    call_command('s3_data_export', id=id, since=since, until=until, limit=limit, type=type)
