from __future__ import unicode_literals, print_function

from django.core.management.base import BaseCommand

from credocommon.models import Detection

from django.core import serializers


class Command(BaseCommand):
    help = "Export detections to file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit", dest="limit", help="Max number of detections to export"
        )

        parser.add_argument("--since", dest="since", help="Export offset")

    def handle(self, *args, **options):
        since = int(options["since"])
        limit = int(options["limit"])

        data = serializers.serialize(
            "json",
            Detection.objects.filter(time_received__gt=since).order_by("time_received")[
                :limit
            ],
        )

        with open("export_{}_{}.json".format(since, limit), "w") as outfile:
            outfile.write(data)
        self.stdout.write("Done!")
