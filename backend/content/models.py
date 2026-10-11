from django.db import models
from django.core.validators import RegexValidator

class Text(models.Model):
    key = models.CharField('Ключ', max_length=120, unique=True)
    section = models.CharField('Раздел', max_length=80)
    label = models.CharField('Название', max_length=250)
    value = models.TextField('Текст', blank=True)
    class Meta:
        verbose_name = 'Текст'; verbose_name_plural = 'Тексты'; ordering = ['section', 'key']
    def __str__(self): return self.label

class Asset(models.Model):
    title = models.CharField('Название', max_length=200)
    filename = models.CharField('Имя файла', max_length=200)
    data = models.BinaryField(editable=False)
    class Meta:
        verbose_name = 'Файл'; verbose_name_plural = 'Файлы'
    def __str__(self): return self.title
    @property
    def url(self): return f'/api/v1/content/files/{self.pk}/'

class Link(models.Model):
    key = models.CharField('Ключ', max_length=120, unique=True)
    label = models.CharField('Название', max_length=200)
    url = models.CharField('Ссылка', max_length=2000, blank=True, validators=[RegexValidator(r'^(https?://|mailto:|tel:|/|#)', 'Используйте https://, http://, mailto:, tel:, / или #.')])
    asset = models.ForeignKey(Asset, verbose_name='Файл вместо ссылки', null=True, blank=True, on_delete=models.SET_NULL)
    class Meta:
        verbose_name = 'Ссылка'; verbose_name_plural = 'Ссылки'; ordering = ['key']
    def __str__(self): return self.label

class FAQ(models.Model):
    question = models.CharField('Вопрос', max_length=300)
    answer = models.TextField('Ответ')
    position = models.PositiveIntegerField('Порядок', default=0)
    active = models.BooleanField('Показывать', default=True)
    class Meta:
        verbose_name = 'Вопрос и ответ'; verbose_name_plural = 'Вопросы и ответы'; ordering = ['position', 'pk']
    def __str__(self): return self.question

class Pricing(models.Model):
    name = models.CharField('Название', max_length=100, default='Тарифы')
    data = models.JSONField('Тарифы')
    class Meta:
        verbose_name = 'Тарифы'; verbose_name_plural = 'Тарифы'
    def __str__(self): return self.name

class Document(models.Model):
    slug = models.SlugField('Адрес', unique=True)
    title = models.CharField('Название', max_length=250)
    body = models.TextField('Содержание', blank=True)
    active = models.BooleanField('Показывать', default=True)
    class Meta:
        verbose_name = 'Документ'; verbose_name_plural = 'Документы'
    def __str__(self): return self.title
