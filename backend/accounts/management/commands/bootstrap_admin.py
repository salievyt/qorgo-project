"""Create the first named administrator from deployment secrets, without resetting existing accounts."""
import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from accounts.models import PrivacySettings


class Command(BaseCommand):
    help = 'Create the initial administrator using BOOTSTRAP_ADMIN_* environment variables.'

    def handle(self, *args, **options):
        username = os.getenv('BOOTSTRAP_ADMIN_USERNAME', '')
        email = os.getenv('BOOTSTRAP_ADMIN_EMAIL', '')
        password = os.getenv('BOOTSTRAP_ADMIN_PASSWORD', '')
        if not all([username, email, password]):
            raise CommandError('Set BOOTSTRAP_ADMIN_USERNAME, BOOTSTRAP_ADMIN_EMAIL and BOOTSTRAP_ADMIN_PASSWORD.')
        User = get_user_model()
        with transaction.atomic():
            existing = User.objects.filter(username=username).first()
            if existing:
                if existing.email != email.lower() or not existing.is_superuser or not existing.is_active:
                    raise CommandError('Existing username belongs to a different or inactive account.')
                self.stdout.write('Administrator already exists; account and password unchanged.')
                return
            if User.objects.filter(email__iexact=email).exists():
                raise CommandError('Email is already registered; no account was changed.')
            user = User(username=username, email=email.lower(), first_name=username,
                        is_staff=True, is_superuser=True, role='admin',
                        privacy_settings=PrivacySettings.objects.create())
            user.set_password(password)
            user.save()
        self.stdout.write(self.style.SUCCESS('Initial administrator created.'))
