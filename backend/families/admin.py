from django.contrib import admin
from qorgo.admin import QorgoAdminLabelsMixin
from .models import Family, FamilyMembership, InviteCode


class FamilyMembershipInline(QorgoAdminLabelsMixin, admin.TabularInline):
    model = FamilyMembership
    extra = 1
    raw_id_fields = ('user',)


@admin.register(Family)
class FamilyAdmin(QorgoAdminLabelsMixin, admin.ModelAdmin):
    list_display = ('name', 'created_by', 'invite_code', 'member_count', 'is_premium', 'created_at')
    list_filter = ('is_premium', 'created_at')
    search_fields = ('name', 'invite_code', 'created_by__phone_number')
    inlines = [FamilyMembershipInline]

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Участники'


@admin.register(FamilyMembership)
class FamilyMembershipAdmin(QorgoAdminLabelsMixin, admin.ModelAdmin):
    list_display = ('family', 'user', 'role', 'joined_at')
    list_filter = ('role',)
    search_fields = ('family__name', 'user__phone_number')


@admin.register(InviteCode)
class InviteCodeAdmin(QorgoAdminLabelsMixin, admin.ModelAdmin):
    list_display = ('code', 'family', 'created_by', 'is_used', 'used_by', 'created_at')
    list_filter = ('is_used',)
