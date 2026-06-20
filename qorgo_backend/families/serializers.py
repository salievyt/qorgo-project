from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Family, FamilyMembership, InviteCode
from accounts.serializers import UserBasicSerializer

User = get_user_model()


class FamilyMemberSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)

    class Meta:
        model = FamilyMembership
        fields = ('id', 'user', 'role', 'joined_at')


class FamilyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = ('name',)


class FamilySerializer(serializers.ModelSerializer):
    members = FamilyMemberSerializer(many=True, read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Family
        fields = (
            'id', 'name', 'created_by', 'members', 'member_count',
            'invite_code', 'is_premium', 'max_members',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'invite_code', 'is_premium', 'created_at', 'updated_at')

    def get_member_count(self, obj):
        return obj.members.count()


class JoinFamilySerializer(serializers.Serializer):
    invite_code = serializers.CharField()
    role = serializers.ChoiceField(
        choices=FamilyMembership.Role.choices,
        default=FamilyMembership.Role.FRIEND,
    )


class UpdateMemberRoleSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    role = serializers.ChoiceField(choices=FamilyMembership.Role.choices)
