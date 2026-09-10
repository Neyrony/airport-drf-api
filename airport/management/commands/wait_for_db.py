import time

from django.core.management import BaseCommand
from django.db import connection, OperationalError
from psycopg import OperationalError as PsycopgOperationalError


class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            try:
                connection.ensure_connection()
                self.stdout.write("Connected to database")
                return
            except (OperationalError, PsycopgOperationalError):
                self.stdout.write("Waiting for database...")
                time.sleep(1)
