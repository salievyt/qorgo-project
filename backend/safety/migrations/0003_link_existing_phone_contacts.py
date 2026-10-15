from django.conf import settings
from django.db import migrations


def link_existing_contacts(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    Contact = apps.get_model('safety', 'Contact')
    database = schema_editor.connection.alias
    users = {str(phone): user_id for phone, user_id in User.objects.using(database).filter(
        phone_number__isnull=False, is_active=True, is_deleted=False,
    ).values_list('phone_number', 'id')}
    linked = set(Contact.objects.using(database).filter(recipient__isnull=False).values_list('owner_id', 'recipient_id'))
    updates = []
    for contact in Contact.objects.using(database).filter(recipient__isnull=True).iterator():
        recipient = users.get(contact.phone)
        if recipient and recipient != contact.owner_id and (contact.owner_id, recipient) not in linked:
            contact.recipient_id = recipient
            updates.append(contact)
            linked.add((contact.owner_id, recipient))
    if updates:
        Contact.objects.using(database).bulk_update(updates, ['recipient'], batch_size=500)


class Migration(migrations.Migration):
    dependencies = [('safety', '0002_contact_recipient_delivery_recipient_and_more')]
    operations = [migrations.RunPython(link_existing_contacts, migrations.RunPython.noop)]
