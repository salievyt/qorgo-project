"""
Qorgo Role-Based Access Control System.

Roles hierarchy:
1. USER (default) — basic app user
2. FAMILY_MEMBER — member of a family group (context-dependent)
3. TRUSTED_CONTACT — emergency contact (may not have an account)
4. EMERGENCY_OPERATOR — future: emergency response center operator
5. ADMIN — platform staff
6. SUPER_ADMIN — technical owner (Django is_superuser)
"""

from enum import Enum


class QorgoRole(str, Enum):
    """System-wide roles stored on the User model."""
    USER = 'user'
    ADMIN = 'admin'
    EMERGENCY_OPERATOR = 'emergency_operator'

    @classmethod
    def choices(cls):
        return [(role.value, role.name.replace('_', ' ').title()) for role in cls]

    @classmethod
    def staff_roles(cls):
        """Roles that grant access to the admin panel."""
        return [cls.ADMIN, cls.EMERGENCY_OPERATOR]


# Context-dependent roles (not stored on User, determined by relationships)
class ContextRole(str, Enum):
    """Roles determined by context, not stored directly."""
    FAMILY_MEMBER = 'family_member'
    TRUSTED_CONTACT = 'trusted_contact'

    @classmethod
    def choices(cls):
        return [(role.value, role.name.replace('_', ' ').title()) for role in cls]


# Mapping of role -> capabilities
ROLE_CAPABILITIES = {
    QorgoRole.USER: [
        'auth:register', 'auth:login',
        'profile:read', 'profile:update',
        'family:create', 'family:join', 'family:leave',
        'sos:create', 'sos:resolve',
        'location:update', 'location:read',
        'geofence:crud',
        'safety_timer:crud',
        'emergency_contact:crud',
        'notification:fcm',
    ],
    QorgoRole.ADMIN: [
        'admin:panel',
        'users:list', 'users:view', 'users:block',
        'sos:view_all', 'sos:moderate',
        'subscriptions:manage',
        'analytics:view',
        'reports:view',
    ],
    QorgoRole.EMERGENCY_OPERATOR: [
        'sos:view_active', 'sos:contact_user', 'sos:confirm_incident',
        'location:view_sos_users',
    ],
}

# SUPER_ADMIN inherits everything via is_superuser
SUPER_ADMIN_CAPABILITIES = [
    'users:manage_roles',
    'infrastructure:access',
    'database:access',
    '*:*',  # Wildcard — all capabilities
]
