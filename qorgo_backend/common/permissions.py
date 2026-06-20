from rest_framework import permissions
from .roles import QorgoRole, ROLE_CAPABILITIES, SUPER_ADMIN_CAPABILITIES


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission to only allow owners of an object to edit it."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, 'user', None) == request.user or getattr(obj, 'created_by', None) == request.user


# ===== Role-based permissions =====

class IsAdmin(permissions.BasePermission):
    """Allow access only to ADMIN or SUPER_ADMIN."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == QorgoRole.ADMIN.value or
            request.user.is_staff or
            request.user.is_superuser
        )


class IsSuperAdmin(permissions.BasePermission):
    """Allow access only to SUPER_ADMIN (is_superuser)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class IsEmergencyOperator(permissions.BasePermission):
    """Allow access to EMERGENCY_OPERATOR and above."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ('emergency_operator', 'admin') or request.user.is_staff or request.user.is_superuser


# ===== Context-dependent permissions =====

class IsPremiumUser(permissions.BasePermission):
    """Allow access only to premium users."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_premium


class IsFamilyCreator(permissions.BasePermission):
    """Allow access only to the family creator."""

    def has_object_permission(self, request, view, obj):
        return getattr(obj, 'created_by', None) == request.user


class IsFamilyMember(permissions.BasePermission):
    """Allow access to family members only."""

    def has_object_permission(self, request, view, obj):
        members = getattr(obj, 'members', None)
        if members is None:
            return False
        return members.filter(id=request.user.id).exists()


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow if user is the object owner OR an admin."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        user_field = getattr(obj, 'user', None) or getattr(obj, 'created_by', None)
        return user_field == request.user
