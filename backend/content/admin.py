from pathlib import Path
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from qorgo.admin import QorgoAdminLabelsMixin
from .models import Text, Link, Asset, FAQ, Pricing, Document


class TextSectionFilter(admin.SimpleListFilter):
    title = 'Раздел сайта'
    parameter_name = 'section'

    def lookups(self, request, model_admin):
        return (
            ('main', 'Главная страница'),
            ('cards', 'Карточки и сценарии'),
            ('pricing', 'Блок тарифов'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(section=self.value())
        return queryset


@admin.register(Text)
class TextAdmin(QorgoAdminLabelsMixin, admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None): return ['key'] if obj else []
    list_display = ['section_name', 'label']; list_filter = [TextSectionFilter]; search_fields = ['label', 'value', 'key']
    fieldsets = (
        ('Расположение на сайте', {'fields': ('key', 'section')}),
        ('Текст для посетителей', {'fields': ('label', 'value')}),
    )
    save_on_top = True
    list_per_page = 50

    @admin.display(description='Раздел сайта', ordering='section')
    def section_name(self, obj):
        return {
            'main': 'Главная страница',
            'cards': 'Карточки и сценарии',
            'pricing': 'Блок тарифов',
        }.get(obj.section, obj.section)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'value' in form.base_fields:
            form.base_fields['value'].help_text = 'Этот текст отображается на лендинге. После сохранения обновите сайт, чтобы увидеть изменение.'
        if 'key' in form.base_fields:
            form.base_fields['key'].help_text = 'Системный адрес текста. Не меняйте его для существующей записи.'
        return form

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
class AssetAdmin(QorgoAdminLabelsMixin, admin.ModelAdmin):
    form = AssetForm; list_display = ['title', 'filename', 'url']; readonly_fields = ['filename', 'url']
    fieldsets = (
        ('Файл для публикации', {'fields': ('title', 'upload')}),
        ('Ссылка для вставки на сайт', {'fields': ('filename', 'url')}),
    )
    save_on_top = True

@admin.register(Link)
class LinkAdmin(QorgoAdminLabelsMixin, admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None): return ['key'] if obj else []
    list_display = ['label', 'url', 'asset']; search_fields = ['label', 'key']
    list_filter = ['asset']
    fieldsets = (
        ('Где используется ссылка', {'fields': ('key', 'label')}),
        ('Куда ведёт', {'fields': ('url', 'asset')}),
    )
    save_on_top = True

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'url' in form.base_fields:
            form.base_fields['url'].help_text = 'Укажите веб-адрес или адрес внутри лендинга. Если выбрали файл ниже, оставьте это поле пустым.'
        if 'asset' in form.base_fields:
            form.base_fields['asset'].help_text = 'Выберите ранее загруженный файл вместо веб-адреса.'
        return form

@admin.register(FAQ)
class FAQAdmin(QorgoAdminLabelsMixin, admin.ModelAdmin):
    list_display = ['question', 'position', 'active']; list_editable = ['position', 'active']
    search_fields = ['question', 'answer']
    fieldsets = (
        ('Вопрос для посетителей сайта', {'fields': ('question', 'answer')}),
        ('Показ на сайте', {'fields': ('position', 'active')}),
    )

@admin.register(Document)
class DocumentAdmin(QorgoAdminLabelsMixin, admin.ModelAdmin):
    list_display = ['title', 'slug', 'active']; prepopulated_fields = {'slug': ['title']}
    list_editable = ['active']
    search_fields = ['title', 'body']
    fieldsets = (
        ('Документ для сайта', {'fields': ('title', 'slug', 'body')}),
        ('Публикация', {'fields': ('active',)}),
    )
    save_on_top = True


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
        self.fields['name'].label = 'Название набора тарифов'
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
class PricingAdmin(QorgoAdminLabelsMixin, admin.ModelAdmin):
    form = PricingEditorForm
    def has_add_permission(self, request): return not Pricing.objects.exists()
    def get_form(self, request, obj=None, **kwargs): return PricingEditorForm
    def get_fields(self, request, obj=None): return list(PricingEditorForm(instance=obj).fields)

    def get_fieldsets(self, request, obj=None):
        form = PricingEditorForm(instance=obj)
        groups = [('Общие сведения', {'fields': ('name', 'notice', 'terms')})]
        plan_fields = [name for name in form.fields if name.startswith('plan_')]
        plan_count = len((obj.data if obj and obj.data else {}).get('plans', []))
        for index in range(plan_count):
            fields = [name for name in plan_fields if name.startswith(f'plan_{index}_')]
            if fields:
                groups.append((f"Тариф {index + 1}", {'fields': fields}))
        return groups

    save_on_top = True
