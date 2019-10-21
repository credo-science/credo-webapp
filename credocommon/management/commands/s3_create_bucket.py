from __future__ import unicode_literals, print_function

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create S3 bucket for file storage"

    def handle(self, *args, **options):
        import boto3

        s3 = boto3.resource(
            "s3",
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            endpoint_url=settings.S3_ENDPOINT_URL,
        )

        s3.meta.client.create_bucket(Bucket=settings.S3_BUCKET)

        self.stdout.write("Created bucket {}".format(settings.S3_BUCKET))
