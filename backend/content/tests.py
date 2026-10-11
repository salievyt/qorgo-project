import io
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient
from .admin import AssetForm, PricingForm
from .models import Text, Link, Asset, FAQ, Document, Pricing

class LandingContentTests(TestCase):
    def setUp(self): self.client = APIClient()
    def test_public_content_tracks_edits_and_hides_drafts(self):
        text = Text.objects.get(key='main.002')
        text.value = 'Новый заголовок'; text.save()
        FAQ.objects.all().update(active=False)
        Document.objects.create(slug='public', title='Документ', body='Текст', active=True)
        response = self.client.get('/api/v1/content/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['texts']['main.002'], 'Новый заголовок')
        self.assertEqual(response.data['faqs'], [])
        self.assertEqual([d['slug'] for d in response.data['documents']], ['public'])
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
    def test_database_file_and_link(self):
        form = AssetForm(data={'title': 'Презентация'}, files={'upload': SimpleUploadedFile('brief.txt', b'hello')})
        self.assertTrue(form.is_valid(), form.errors)
        asset = form.save()
        Link.objects.filter(key='presentation').update(asset=asset)
        content = self.client.get('/api/v1/content/').data
        self.assertTrue(content['presentation_url'].endswith(asset.url))
        response = self.client.get(asset.url)
        self.assertEqual(b''.join(response.streaming_content), b'hello')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
    def test_upload_limits_and_missing_file(self):
        self.assertFalse(AssetForm(data={'title': 'Empty'}).is_valid())
        form = AssetForm(data={'title': 'Large'}, files={'upload': SimpleUploadedFile('large.bin', b'x' * (4 * 1024 * 1024 + 1))})
        self.assertFalse(form.is_valid())
    def test_malformed_pricing_rejected(self):
        form = PricingForm(data={'name': 'Тарифы', 'data': '{"plans": [{}]}'})
        self.assertFalse(form.is_valid())
    def test_api_does_not_allow_public_edits(self):
        self.assertEqual(self.client.post('/api/v1/content/', {'texts': {}}, format='json').status_code, 405)
    def test_staff_can_edit_pricing_and_upload_files_in_admin(self):
        from accounts.models import User
        user = User.objects.create(username='content-editor', email='editor@example.com', is_staff=True, is_superuser=True)
        self.client.force_login(user)
        pricing = Pricing.objects.first()
        response = self.client.get(f'/admin/content/pricing/{pricing.pk}/change/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'plan_0_monthly')
        response = self.client.get('/admin/content/asset/add/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="upload"')
    def test_pricing_editor_keeps_plan_ids_and_updates_values(self):
        from .admin import PricingEditorForm
        pricing = Pricing.objects.first()
        data = {'name': pricing.name, 'notice': 'Новое примечание', 'terms': 'Условия'}
        for index, plan in enumerate(pricing.data['plans']):
            for key in ['name', 'audience', 'monthly', 'annual', 'features', 'planned']:
                data[f'plan_{index}_{key}'] = '\n'.join(plan[key]) if isinstance(plan[key], list) else plan[key]
        data['plan_1_monthly'] = 250
        form = PricingEditorForm(data=data, instance=pricing)
        self.assertTrue(form.is_valid(), form.errors)
        form.save(); pricing.refresh_from_db()
        self.assertEqual(pricing.data['plans'][1]['monthly'], 250)
        self.assertEqual(pricing.data['plans'][1]['id'], 'premium')
