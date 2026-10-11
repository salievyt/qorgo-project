import time
from django.core.management.base import BaseCommand
from django.db import close_old_connections
from safety.services import process_deadlines, process_deliveries
class Command(BaseCommand):
    help = 'Process persistent journey deadlines and outgoing SOS messages.'
    def add_arguments(self, parser):
        parser.add_argument('--once', action='store_true')
    def handle(self, *args, **options):
        while True:
            close_old_connections()
            process_deadlines()
            process_deliveries()
            if options['once']:
                return
            time.sleep(2)
