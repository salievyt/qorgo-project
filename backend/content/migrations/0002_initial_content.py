import json
from pathlib import Path
from django.db import migrations


def seed(apps, schema_editor):
    data = json.loads(Path(__file__).with_name('initial_content.json').read_text())
    database = schema_editor.connection.alias
    for item in data['texts']:
        apps.get_model('content', 'Text').objects.using(database).get_or_create(key=item['key'], defaults={k: v for k, v in item.items() if k != 'key'})
    for key, url in data['links'].items():
        labels = {'presentation': 'Презентация QORGO', 'link.1': 'Перейти к содержанию', 'link.2': 'Логотип в шапке', 'link.3': 'О проекте в шапке', 'link.4': 'Познакомиться с QORGO', 'link.5': 'Как работает', 'link.6': 'Пилот: связаться', 'link.7': 'Узнать о проекте', 'link.8': 'Логотип в подвале', 'link.9': 'Подвал: возможности', 'link.10': 'Подвал: пилот', 'link.11': 'Подвал: FAQ', 'link.12': 'Наверх'}
        label = labels.get(key, f'Навигация: {key}')
        apps.get_model('content', 'Link').objects.using(database).get_or_create(key=key, defaults={'label': label, 'url': url})
    for position, (question, answer) in enumerate(data['faqs']):
        apps.get_model('content', 'FAQ').objects.using(database).get_or_create(question=question, defaults={'answer': answer, 'position': position})
    apps.get_model('content', 'Pricing').objects.using(database).get_or_create(name='Тарифы', defaults={'data': data['pricing']})
    for document in data['documents']:
        apps.get_model('content', 'Document').objects.using(database).get_or_create(slug=document['slug'], defaults={'title': document['title'], 'body': document['body'], 'active': False})


class Migration(migrations.Migration):
    dependencies = [('content', '0001_initial')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
