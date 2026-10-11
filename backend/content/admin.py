from pathlib import Path
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Text, Link, Asset, FAQ, Pricing, Document

@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None): return ['key'] if obj else []
    list_display = ['label', 'section', 'key']; list_filter = ['section']; search_fields = ['label', 'value', 'key']

class AssetForm(forms.ModelForm):
    upload = forms.FileField(label='Загрузить файл', required=False, help_text='До 4 МБ. Файл сохраняется в базе данных.')
    class Meta:
        model = Asset; fields = ['title', 'upload']
    def clean_upload(self):
        upload = self.cleaned_data.get('upload')
        if not upload and not self.instance.pk: raise ValidationError('Выберите файл.')
        if upload and upload.size > 4 * 1024 * 1024: raise ValidationError('Максимальный размер — 4 МБ.')
        return upload
    def save(self, commit=True):
        obj = super().save(commit=False)
        upload = self.cleaned_data.get('upload')
        if upload:
            obj.filename = Path(upload.name).name[:200]; obj.data = upload.read()
        if commit: obj.save()
        return obj

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    form = AssetForm; list_display = ['title', 'filename', 'url']; readonly_fields = ['filename', 'url']

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None): return ['key'] if obj else []
    list_display = ['label', 'key', 'url', 'asset']; search_fields = ['label', 'key']

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'position', 'active']; list_editable = ['position', 'active']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'active']; prepopulated_fields = {'slug': ['title']}


class PricingForm(forms.ModelForm):
    class Meta:
        model = Pricing
        fields = '__all__'
    def clean_data(self):
        data = self.cleaned_data['data']
        if not isinstance(data, dict) or not isinstance(data.get('plans'), list):
            raise ValidationError('Тарифы должны содержать список plans.')
        if not all(isinstance(data.get(key), str) for key in ['currency', 'notice', 'terms']):
            raise ValidationError('Укажите строки currency, notice и terms.')
        ids = set()
        for plan in data['plans']:
            if not isinstance(plan, dict) or not all(isinstance(plan.get(key), str) for key in ['id', 'name', 'audience']):
                raise ValidationError('Каждый тариф должен содержать id, name и audience.')
            if plan['id'] in ids: raise ValidationError('Идентификаторы тарифов должны быть уникальными.')
            ids.add(plan['id'])
            for key in ['monthly', 'annual']:
                if type(plan.get(key)) not in (int, float) or plan[key] < 0: raise ValidationError('Цена должна быть неотрицательным числом.')
            for key in ['features', 'planned']:
                if not isinstance(plan.get(key), list) or not all(isinstance(x, str) for x in plan[key]): raise ValidationError('features и planned должны быть списками текстов.')
        return data

class PricingEditorForm(PricingForm):
    class Meta:
        model = Pricing
        fields = ['name']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data = self.instance.data or {'currency': 'KGS', 'notice': '', 'terms': '', 'plans': []}
        for key, label in [('notice', 'Примечание'), ('terms', 'Условия')]:
            self.fields[key] = forms.CharField(label=label, widget=forms.Textarea, required=False, initial=data.get(key, ''))
        for index, plan in enumerate(data.get('plans', [])):
            title = plan['name']
            for key, label in [('name', 'Название'), ('audience', 'Для кого')]:
                self.fields[f'plan_{index}_{key}'] = forms.CharField(label=f'{title}: {label}', initial=plan[key])
            for key, label in [('monthly', 'Цена за месяц'), ('annual', 'Цена за год')]:
                self.fields[f'plan_{index}_{key}'] = forms.IntegerField(label=f'{title}: {label}', min_value=0, initial=plan[key])
            for key, label in [('features', 'Доступные возможности'), ('planned', 'Планируемые возможности')]:
                self.fields[f'plan_{index}_{key}'] = forms.CharField(label=f'{title}: {label}', widget=forms.Textarea, required=False, initial='\n'.join(plan[key]), help_text='Одна возможность на строку.')
    def save(self, commit=True):
        import copy
        obj = super().save(commit=False)
        data = copy.deepcopy(self.instance.data or {'currency': 'KGS', 'plans': []})
        for key in ['notice', 'terms']: data[key] = self.cleaned_data[key]
        for index, plan in enumerate(data['plans']):
            for key in ['name', 'audience', 'monthly', 'annual', 'features', 'planned']:
                value = self.cleaned_data[f'plan_{index}_{key}']
                plan[key] = [line.strip() for line in value.splitlines() if line.strip()] if key in ['features', 'planned'] else value
        obj.data = data
        if commit: obj.save()
        return obj


@admin.register(Pricing)
class PricingAdmin(admin.ModelAdmin):
    form = PricingEditorForm
    def has_add_permission(self, request): return not Pricing.objects.exists()
    def get_form(self, request, obj=None, **kwargs): return PricingEditorForm
    def get_fields(self, request, obj=None): return list(PricingEditorForm(instance=obj).fields)
