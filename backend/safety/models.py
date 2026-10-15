from django.conf import settings
from django.db import models

class Contact(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='trusted_by_contacts')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    relationship = models.CharField(max_length=60, blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['owner', 'phone'], name='unique_contact_phone'), models.UniqueConstraint(fields=['owner', 'recipient'], condition=models.Q(recipient__isnull=False), name='unique_contact_recipient')]

class Alert(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    request_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=20, default='sos')
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    location_at = models.DateTimeField(null=True)
    location_accuracy = models.FloatField(null=True)
    resolved_at = models.DateTimeField(null=True)
    assigned_operator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='safety_assigned_incidents')
    assigned_at = models.DateTimeField(null=True, blank=True)
    operator_note = models.TextField(blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['owner', 'request_id'], name='idempotent_alert')]

class Delivery(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='received_safety_deliveries')
    alert = models.ForeignKey(Alert, related_name='deliveries', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    # "accepted" means provider accepted the request, not recipient received it.
    status = models.CharField(max_length=24, default='pending')
    channel = models.CharField(max_length=10, blank=True)
    provider_id = models.CharField(max_length=100, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

class Journey(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    destination = models.CharField(max_length=160)
    deadline = models.DateTimeField()
    state = models.CharField(max_length=16, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    alert = models.OneToOneField(Alert, null=True, on_delete=models.SET_NULL)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['owner'], condition=models.Q(state='active'), name='one_active_journey')]
