import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from common.models import TimeStampedModel


class UserManager(BaseUserManager):
    """Custom manager for User model (no username field)."""
    use_in_migrations = True

    def _create_user(self, phone_number, password, **extra_fields):
        """Create and save a user with the given phone number and password."""
        if not phone_number:
            raise ValueError('The phone number must be set')
        email = extra_fields.pop('email', None)
        if email:
            email = self.normalize_email(email)
        user = self.model(
            phone_number=phone_number,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(phone_number, password, **extra_fields)


class PrivacySettings(models.Model):
    """Privacy settings for user profile and location visibility."""
    class LocationVisibility(models.TextChoices):
        FAMILY = 'family', _('Family Only')
        CONTACTS = 'contacts', _('Emergency Contacts Only')
        NOBODY = 'nobody', _('Nobody')

    show_location = models.BooleanField(default=True, verbose_name=_('Show location'))
    location_visibility = models.CharField(
        max_length=20,
        choices=LocationVisibility.choices,
        default=LocationVisibility.FAMILY,
        verbose_name=_('Location visibility'),
    )
    show_profile = models.BooleanField(default=True, verbose_name=_('Show profile'))
    share_battery_level = models.BooleanField(default=True, verbose_name=_('Share battery level'))
    share_speed = models.BooleanField(default=True, verbose_name=_('Share speed'))
    share_with_operators = models.BooleanField(default=False, verbose_name=_('Share location with operators'))

    class Meta:
        verbose_name = _('Privacy settings')
        verbose_name_plural = _('Privacy settings')


class DeviceInfo(models.Model):
    """Device information for push notifications and analytics."""
    class Platform(models.TextChoices):
        IOS = 'ios', _('iOS')
        ANDROID = 'android', _('Android')

    platform = models.CharField(max_length=10, choices=Platform.choices, verbose_name=_('Platform'))
    device_model = models.CharField(max_length=255, blank=True, verbose_name=_('Device model'))
    os_version = models.CharField(max_length=50, blank=True, verbose_name=_('OS version'))
    app_version = models.CharField(max_length=20, blank=True, verbose_name=_('App version'))
    battery_level = models.FloatField(default=100.0, verbose_name=_('Battery level'))
    is_low_power_mode = models.BooleanField(default=False, verbose_name=_('Low power mode'))
    fcm_token = models.TextField(blank=True, null=True, verbose_name=_('FCM token'))

    class Meta:
        verbose_name = _('Device info')
        verbose_name_plural = _('Device info')


class User(AbstractUser):
    """Custom user model for Qorgo with extended profile fields."""
    class Gender(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        OTHER = 'other', _('Other')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = PhoneNumberField(unique=True, null=True, blank=True, verbose_name=_('Phone number'))
    email = models.EmailField(unique=True, verbose_name=_('Email'))
    first_name = models.CharField(max_length=150, verbose_name=_('First name'))
    last_name = models.CharField(max_length=150, verbose_name=_('Last name'))
    photo = models.ImageField(upload_to='users/photos/', blank=True, null=True, verbose_name=_('Photo'))
    date_of_birth = models.DateField(blank=True, null=True, verbose_name=_('Date of birth'))
    gender = models.CharField(max_length=10, choices=Gender.choices, blank=True, null=True, verbose_name=_('Gender'))
    city = models.CharField(max_length=150, blank=True, verbose_name=_('City'))
    blood_type = models.CharField(max_length=10, blank=True, verbose_name=_('Blood type'))
    medical_notes = models.TextField(blank=True, verbose_name=_('Medical notes'))
    is_premium = models.BooleanField(default=False, verbose_name=_('Premium'))
    premium_expiry = models.DateTimeField(blank=True, null=True, verbose_name=_('Premium expiry'))
    last_active_at = models.DateTimeField(auto_now=True, verbose_name=_('Last active'))
    is_deleted = models.BooleanField(default=False, verbose_name=_('Deleted'))

    # Relations
    privacy_settings = models.OneToOneField(
        PrivacySettings, on_delete=models.CASCADE,
        related_name='user', blank=True, null=True,
        verbose_name=_('Privacy settings'),
    )
    devices = models.ManyToManyField(DeviceInfo, blank=True, related_name='users', verbose_name=_('Devices'))

    # Emergency contacts
    emergency_contacts = models.ManyToManyField(
        'self', through='EmergencyContact',
        symmetrical=False, blank=True,
        verbose_name=_('Emergency contacts'),
    )

    # FCM tokens list for push notifications
    fcm_tokens = models.JSONField(default=list, blank=True, verbose_name=_('FCM tokens'))

    # Qorgo Role
    role = models.CharField(
        max_length=30,
        choices=[
            ('user', 'User'),
            ('admin', 'Admin'),
            ('emergency_operator', 'Emergency Operator'),
        ],
        default='user',
        verbose_name=_('Role'),
        db_index=True,
    )

    # Required fields
    # Optional login for administrators; mobile accounts still identify by phone.
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = UserManager()

    @property
    def display_role(self) -> str:
        """Return the human-readable role name."""
        if self.is_superuser:
            return 'super_admin'
        return self.role

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == 'admin' or self.is_staff

    @property
    def is_emergency_operator(self) -> bool:
        """Check if user is an emergency operator."""
        return self.role == 'emergency_operator'

    def has_capability(self, capability: str) -> bool:
        """Check if user has a specific capability."""
        from common.roles import ROLE_CAPABILITIES, SUPER_ADMIN_CAPABILITIES

        if self.is_superuser:
            return True

        caps = ROLE_CAPABILITIES.get(self.role, [])
        return capability in caps

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.phone_number})'


class EmergencyContact(models.Model):
    """Through model for user emergency contacts."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emergency_contact_relations', verbose_name=_('User'))
    contact = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact_of', verbose_name=_('Contact'))
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    phone_number = PhoneNumberField(verbose_name=_('Phone number'))
    relationship = models.CharField(max_length=100, verbose_name=_('Relationship'))
    priority = models.PositiveSmallIntegerField(default=1, verbose_name=_('Priority'))
    is_verified = models.BooleanField(default=False, verbose_name=_('Verified'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    class Meta:
        verbose_name = _('Emergency contact')
        verbose_name_plural = _('Emergency contacts')
        ordering = ['priority']

    def __str__(self):
        return f'{self.name} ({self.phone_number})'
