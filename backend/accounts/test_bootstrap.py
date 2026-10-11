import os
from io import StringIO
from unittest.mock import patch
from django.contrib.auth import authenticate, get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase


class BootstrapAdminTests(TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'BOOTSTRAP_ADMIN_USERNAME': 'initial_admin', 'BOOTSTRAP_ADMIN_EMAIL': 'initial@example.invalid', 'BOOTSTRAP_ADMIN_PASSWORD': 'Initial-82-Strong!'})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_named_admin_can_sign_in_without_phone(self):
        call_command('bootstrap_admin', stdout=StringIO())
        user = get_user_model().objects.get(username='initial_admin')
        self.assertTrue(user.is_superuser and user.is_staff)
        self.assertIsNone(user.phone_number)
        self.assertEqual(authenticate(username='initial_admin', password='Initial-82-Strong!'), user)
        response = self.client.post('/admin/login/?next=/admin/', {'username': 'initial_admin', 'password': 'Initial-82-Strong!', 'next': '/admin/'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.get('/admin/').status_code, 200)

    def test_repeated_bootstrap_never_resets_password(self):
        call_command('bootstrap_admin', stdout=StringIO())
        user = get_user_model().objects.get(username='initial_admin')
        user.set_password('Changed-93-Strong!')
        user.save()
        call_command('bootstrap_admin', stdout=StringIO())
        user.refresh_from_db()
        self.assertTrue(user.check_password('Changed-93-Strong!'))
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_existing_email_is_not_promoted(self):
        user = get_user_model().objects.create_user(phone_number='+996700000044', email='initial@example.invalid', password='User-93-Strong!')
        with self.assertRaises(CommandError):
            call_command('bootstrap_admin', stdout=StringIO())
        user.refresh_from_db()
        self.assertFalse(user.is_superuser)
        self.assertIsNone(user.username)
