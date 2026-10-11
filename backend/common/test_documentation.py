from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.template.loader import get_template
from django.test import TestCase
from django.utils import timezone
from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.validation import validate_schema
from safety.models import Journey, Alert


class DocumentationTests(TestCase):
    def test_swagger_and_redoc_use_local_assets(self):
        for path in ['/api/docs/', '/api/swagger/', '/api/redoc/']:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '/static/drf_spectacular_sidecar/')
        self.assertIsNotNone(finders.find('drf_spectacular_sidecar/swagger-ui-dist/swagger-ui-bundle.js'))

    def test_schema_covers_both_apis_without_changing_timers(self):
        user = get_user_model().objects.create_user(phone_number='+996700000030', email='schema@example.invalid', password='Qorgo-82-Strong!')
        journey = Journey.objects.create(owner=user, destination='Home', deadline=timezone.now() - timedelta(minutes=1))
        schema = SchemaGenerator().get_schema(public=True)
        validate_schema(schema)
        for path in ['/api/register/', '/api/alerts/', '/api/journeys/', '/api/v1/auth/login/', '/api/v1/safety-timers/create/']:
            self.assertIn(path, schema['paths'])
        self.assertIn('requestBody', schema['paths']['/api/register/']['post'])
        security = schema['components']['securitySchemes']
        self.assertIn('tokenAuth', security)
        self.assertIn('jwtAuth', security)
        self.assertIn('MobileAlert', schema['components']['schemas'])
        self.assertIn('Alert', schema['components']['schemas'])
        journey.refresh_from_db()
        self.assertEqual(journey.state, 'active')
        self.assertFalse(Alert.objects.exists())
        self.assertEqual(self.client.get('/api/schema/').status_code, 200)

    def test_jazzmin_admin_login_and_dashboard(self):
        self.assertIn('jazzmin', get_template('admin/base.html').origin.name)
        self.assertEqual(self.client.get('/admin/login/').status_code, 200)
        self.assertEqual(self.client.get('/admin/').status_code, 302)
        user = get_user_model().objects.create_superuser(phone_number='+996700000031', email='admin@example.invalid', password='Qorgo-82-Strong!', first_name='Admin', last_name='User')
        self.client.force_login(user)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'QORGO')
        self.assertContains(response, '/api/docs/')
