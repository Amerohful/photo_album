from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Load fake data'

    def handle(self, *args, **options):
        call_command('loaddata', 'mails.json')
        call_command('loaddata', 'users.json')
        call_command('loaddata', 'photos.json')
