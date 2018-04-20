from django.core.management.base import BaseCommand, CommandError
from credoapi.models import User, Team, Detection, Device

from random import choice, random, randint
from time import time
import string
import base64

PARTICLE_IMG = """
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
gg==
"""


class Command(BaseCommand):
    help = 'Add sample data to db'

    @staticmethod
    def generate_random_string(n):
        return ''.join(choice(string.ascii_lowercase + string.digits) for _ in range(n))

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            help='Force adding of sample data'
        )

    def generate_sample_data(self):

        teams = []
        devices = []
        users = []
        team_count = 3
        user_count = 10
        detection_count = 100

        if not User.objects.filter(username='admin'):
            User.objects.create_superuser(
                email='admin@email.com',
                username='admin',
                display_name='Admin',
                password='adminpassword',
                key='adminkey1234',
            )

        for i in range(team_count):
            teams += [Team.objects.create(name='team%02d' % i)]

        for i in range(user_count):
            users += [User.objects.create_user(
                email='user%02d@email.com' % i,
                username='user%02d' % i,
                display_name='User%02d' % i,
                password='password%02d' % i,
                key='aaaa%02d' % i,
                team=choice(teams)
            )]

        for i in range(user_count):
            devices += [Device.objects.create(
                device_id=(self.generate_random_string(8)),
                device_model='galaxy s%d' % i,
                android_version='23-6.0',
                user=users[i]
            )]

        for i in range(detection_count):
            Detection.objects.create(
                accuracy=1.0,
                altitude=100.0 + random() * 100,
                frame_content=bytearray(base64.decodestring(PARTICLE_IMG)),
                height=100,
                width=100,
                d_id=randint(0, 10000),
                latitude=15.0 + random() * 10,
                longitude=45.0 + random() * 10,
                provider='gps',
                timestamp=int(time() - 5000 + random() * 10000),
                device=choice(devices),
                user=choice(users)
            )

    def handle(self, *args, **options):
        user_count = User.objects.count()

        if user_count != 0 and not options['force']:
            self.stdout.write('DB already contains data! Use --force to override this check.')
            return

        self.stdout.write("Generating sample data...")
        self.generate_sample_data()
        self.stdout.write("Done!")
