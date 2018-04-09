from django.core.management.base import BaseCommand, CommandError
from credoapi.models import User, Team, Detection, Device


class Command(BaseCommand):
    help = 'Add sample data to db'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            help='Force adding of sample data'
        )

    def handle(self, *args, **options):
        user_count = User.objects.count()

        if user_count != 0 and not options['force']:
            self.stdout.write("DB already contains data! Use --force to override this check.")
