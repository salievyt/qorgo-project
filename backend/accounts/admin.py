from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from qorgo.admin import QorgoAdminLabelsMixin
from .models import User, EmergencyContact, PrivacySettings, DeviceInfo
from .forms import QorgoAdminAuthenticationForm

admin.site.login_form = QorgoAdminAuthenticationForm


class EmergencyContactInline(admin.TabularInline):
    model = EmergencyContact
    fk_name = 'user'
    extra = 1


@admin.register(User)
class UserAdmin(QorgoAdminLabelsMixin, BaseUserAdmin):
    list_display = ('username', 'phone_number', 'email', 'first_name', 'last_name', 'role', 'is_premium', 'is_active', 'last_active_at')
    list_filter = ('role', 'is_premium', 'gender', 'city', 'is_active', 'date_joined')
    search_fields = ('username', 'phone_number', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    inlines = [EmergencyContactInline]

    fieldsets = (
        ('Вход в аккаунт', {'fields': ('username', 'phone_number', 'password')}),
        ('Профиль пользователя', {
            'fields': (
                'email', 'first_name', 'last_name', 'photo',
                'date_of_birth', 'gender', 'city', 'blood_type', 'medical_notes'
            )
        }),
        ('Приватность', {'fields': ('privacy_settings',)}),
        ('Доступ и подписка', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_premium', 'premium_expiry', 'groups', 'user_permissions'),
        }),
        ('Даты и активность', {'fields': ('last_login', 'date_joined', 'last_active_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone_number', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(EmergencyContact)
class EmergencyContactAdmin(QorgoAdminLabelsMixin, admin.ModelAdmin):
    list_display = ('user', 'name', 'phone_number', 'relationship', 'priority', 'is_verified')
    list_filter = ('relationship', 'is_verified')
    search_fields = ('user__phone_number', 'name', 'phone_number')


@admin.register(PrivacySettings)
class PrivacySettingsAdmin(QorgoAdminLabelsMixin, admin.ModelAdmin):
    list_display = ('id', 'show_location', 'location_visibility', 'show_profile')
    list_filter = ('location_visibility',)


@admin.register(DeviceInfo)
class DeviceInfoAdmin(QorgoAdminLabelsMixin, admin.ModelAdmin):
    list_display = ('platform', 'device_model', 'os_version', 'app_version', 'battery_level')
    list_filter = ('platform',)
