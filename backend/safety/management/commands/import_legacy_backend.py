"""Copy the original MVP SQLite data into a fresh unified database."""
import sqlite3
import uuid
from datetime import timezone as datetime_timezone
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.db import connection, transaction
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from rest_framework.authtoken.models import Token
from accounts.models import PrivacySettings
from safety.models import Contact, Alert, Delivery, Journey


class Command(BaseCommand):
    help = 'Import MVP users, tokens and safety data into an empty unified database; source is read-only.'

    def add_arguments(self, parser):
        parser.add_argument('source', type=Path)

    def handle(self, *args, **options):
        source = options['source'].resolve()
        if not source.is_file():
            raise CommandError('Source SQLite database does not exist.')
        target = connection.settings_dict['NAME']
        if connection.vendor == 'sqlite' and Path(target).resolve() == source:
            raise CommandError('Source and target must be different databases.')
        User = get_user_model()
        with transaction.atomic():
            if any(model.objects.exists() for model in [User, Contact, Alert, Delivery, Journey, Token]):
                raise CommandError('Target must be empty. Import was not performed.')
            try:
                with sqlite3.connect(source.as_uri() + '?mode=ro', uri=True) as legacy:
                    legacy.row_factory = sqlite3.Row
                    rows = {name: [dict(row) for row in legacy.execute(f'SELECT * FROM {name}')]
                            for name in ['auth_user', 'authtoken_token', 'safety_contact',
                                         'safety_alert', 'safety_delivery', 'safety_journey']}
            except sqlite3.DatabaseError as exc:
                raise CommandError(f'Invalid legacy database: {exc}') from exc
            users = {}
            for row in rows['auth_user']:
                email = (row['email'] or row['username']).lower()
                if User.objects.filter(email=email).exists():
                    raise CommandError('Legacy users have duplicate emails; import rolled back.')
                user = User.objects.create(
                    id=uuid.uuid5(uuid.NAMESPACE_URL, f'qorgo/legacy-user/{row["id"]}'),
                    email=email, password=row['password'], first_name=row['first_name'],
                    last_name=row['last_name'], is_active=row['is_active'],
                    is_staff=row['is_staff'], is_superuser=row['is_superuser'],
                    date_joined=self.datetime(row['date_joined']),
                    last_login=self.datetime(row['last_login']),
                    privacy_settings=PrivacySettings.objects.create(),
                )
                users[row['id']] = user.pk
            for row in rows['authtoken_token']:
                token = Token.objects.create(key=row['key'], user_id=users[row['user_id']])
                Token.objects.filter(pk=token.pk).update(created=self.datetime(row['created']))
            for table, model in [('safety_contact', Contact), ('safety_alert', Alert),
                                 ('safety_delivery', Delivery), ('safety_journey', Journey)]:
                date_fields = {field.name for field in model._meta.fields if field.get_internal_type() == 'DateTimeField'}
                for row in rows[table]:
                    if 'owner_id' in row:
                        row['owner_id'] = users[row['owner_id']]
                    dates = {key: self.datetime(row[key]) for key in date_fields}
                    values = {**row, **dates}
                    instance = model.objects.create(**values)
                    # Preserve auto_now/auto_now_add timestamps from the original database.
                    if dates:
                        model.objects.filter(pk=instance.pk).update(**dates)
            with connection.cursor() as cursor:
                for sql in connection.ops.sequence_reset_sql(no_style(), [Contact, Alert, Delivery, Journey]):
                    cursor.execute(sql)
        self.stdout.write(self.style.SUCCESS(
            f'Imported {len(users)} users and legacy safety data. Source database was unchanged.'
        ))

    @staticmethod
    def datetime(value):
        if value is None:
            return None
        parsed = parse_datetime(value)
        return timezone.make_aware(parsed, datetime_timezone.utc) if timezone.is_naive(parsed) else parsed
