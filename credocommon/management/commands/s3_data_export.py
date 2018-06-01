from __future__ import unicode_literals, print_function

import base64
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from credocommon.models import Detection, Ping


def gen(data):
    for d in data:
        if d.get('frame_content'):
            d['frame_content'] = base64.b64encode(d['frame_content'])
        yield d


class Command(BaseCommand):
    help = 'Export detections to file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            dest='type',
            help='Type of event to export (detection/ping)'
        )

        parser.add_argument(
            '--since',
            dest='since',
            type=int,
            help='Export events that have time_received greater than specified value'
        )

        parser.add_argument(
            '--until',
            dest='until',
            type=int,
            help='Export events that have time_received lower than specified value'
        )

        parser.add_argument(
            '--limit',
            dest='limit',
            type=int,
            help='Maximum number of events to export'
        )

        parser.add_argument(
            '--id',
            dest='id',
            help='Job ID'
        )

    def handle(self, *args, **options):
        import boto3
        import simplejson

        filename = 'export_{}.json'.format(options['id'])

        models = {
            'detection': Detection,
            'ping': Ping
        }

        data = models[options['type']].objects.order_by('time_received')\
                                      .filter(time_received__gt=options['since'])\
                                      .filter(time_received__lte=options['until'])[:options['limit']]

        s3 = boto3.resource(
            's3',
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            endpoint_url=settings.S3_ENDPOINT_URL
        )

        with open(filename, 'w') as outfile:
            for chunk in simplejson.JSONEncoder(iterable_as_array=True).iterencode(gen(data.values())):
                outfile.write(chunk)

        bucket = s3.Bucket(settings.S3_BUCKET)

        bucket.upload_file(filename, filename)

        os.remove(filename)

        self.stdout.write('Finished data export {]'.format(options['id']))
