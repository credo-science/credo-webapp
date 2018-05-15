from django.core.management.base import BaseCommand

from credocommon.models import Detection
from credocommon.helpers import validate_image

class Command(BaseCommand):
    help = 'Add sample data to db'

    def handle(self, *args, **options):
        detections = Detection.objects.all()

        for d in detections:
            if (not d.frame_content) or validate_image(d.frame_content):
                self.stdout.write("Processing image %s" % d.id)
                d.visible = False
                d.save()

        self.stdout.write("Done!")
