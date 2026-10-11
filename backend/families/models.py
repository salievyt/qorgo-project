import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Family(models.Model):
    """Family/group for safety circle."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name=_('Family name'))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='created_families', verbose_name=_('Created by'),
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='FamilyMembership',
        through_fields=('family', 'user'),
        related_name='families', verbose_name=_('Members'),
    )
    invite_code = models.CharField(max_length=20, unique=True, verbose_name=_('Invite code'))
    is_premium = models.BooleanField(default=False, verbose_name=_('Premium'))
    max_members = models.PositiveSmallIntegerField(default=5, verbose_name=_('Max members'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    class Meta:
        verbose_name = _('Family')
        verbose_name_plural = _('Families')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.members.count()} members)'


class FamilyMembership(models.Model):
    """Through model for family membership with roles."""
    class Role(models.TextChoices):
        CREATOR = 'creator', _('Creator')
        PARENT = 'parent', _('Parent')
        CHILD = 'child', _('Child')
        SPOUSE = 'spouse', _('Spouse')
        RELATIVE = 'relative', _('Relative')
        FRIEND = 'friend', _('Friend')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, verbose_name=_('Family'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('User'))
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.FRIEND, verbose_name=_('Role'))
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='invited_memberships', verbose_name=_('Invited by'),
    )
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Joined at'))

    class Meta:
        verbose_name = _('Family membership')
        verbose_name_plural = _('Family memberships')
        unique_together = ('family', 'user')

    def __str__(self):
        return f'{self.user} — {self.role} in {self.family.name}'


class InviteCode(models.Model):
    """Track invite codes and their usage."""
    code = models.CharField(max_length=20, primary_key=True, verbose_name=_('Code'))
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='invite_codes', verbose_name=_('Family'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Created by'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    is_used = models.BooleanField(default=False, verbose_name=_('Used'))
    used_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='used_invite_codes', verbose_name=_('Used by'),
    )
    used_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Used at'))

    class Meta:
        verbose_name = _('Invite code')
        verbose_name_plural = _('Invite codes')

    def __str__(self):
        return f'{self.code} — {self.family.name}'
