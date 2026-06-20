from django.db import transaction
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import Family, FamilyMembership, InviteCode
from .serializers import (
    FamilyCreateSerializer, FamilySerializer,
    JoinFamilySerializer, FamilyMemberSerializer,
    UpdateMemberRoleSerializer,
)
from common.services import generate_invite_code
from common.permissions import IsFamilyCreator
from notifications.services import send_push_notification


@extend_schema(summary='Create a family group', tags=['Family'])
class CreateFamilyView(generics.CreateAPIView):
    serializer_class = FamilyCreateSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        family = serializer.save(created_by=self.request.user)

        # Generate unique invite code
        invite_code = generate_invite_code()
        while Family.objects.filter(invite_code=invite_code).exists():
            invite_code = generate_invite_code()
        family.invite_code = invite_code
        family.save(update_fields=['invite_code'])

        # Add creator as member
        FamilyMembership.objects.create(
            family=family,
            user=self.request.user,
            role=FamilyMembership.Role.CREATOR,
            invited_by=self.request.user,
        )

        # Create invite code record
        InviteCode.objects.create(
            code=invite_code,
            family=family,
            created_by=self.request.user,
        )


@extend_schema(summary='List user families', tags=['Family'])
class UserFamiliesView(generics.ListAPIView):
    serializer_class = FamilySerializer

    def get_queryset(self):
        return Family.objects.filter(members=self.request.user)


@extend_schema(summary='Get family details', tags=['Family'])
class FamilyDetailView(generics.RetrieveAPIView):
    serializer_class = FamilySerializer

    def get_queryset(self):
        return Family.objects.filter(members=self.request.user)


@extend_schema(summary='Join family with invite code', tags=['Family'])
class JoinFamilyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = JoinFamilySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['invite_code'].upper().strip()
        role = serializer.validated_data['role']

        try:
            invite = InviteCode.objects.get(code=code, is_used=False)
        except InviteCode.DoesNotExist:
            return Response({'error': 'Invalid or expired invite code.'}, status=status.HTTP_400_BAD_REQUEST)

        family = invite.family

        # Check if user is already a member
        if FamilyMembership.objects.filter(family=family, user=request.user).exists():
            return Response({'error': 'Already a member of this family.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check member limit
        if family.members.count() >= family.max_members:
            return Response({'error': 'Family has reached maximum members.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            FamilyMembership.objects.create(
                family=family,
                user=request.user,
                role=role,
                invited_by=invite.created_by,
            )
            invite.is_used = True
            invite.used_by = request.user
            invite.save()

        # Notify family members
        for member in family.members.exclude(id=request.user.id):
            send_push_notification(
                member,
                '👋 New Family Member',
                f'{request.user.first_name} {request.user.last_name} has joined {family.name}!',
                {'type': 'family_join', 'family_id': str(family.id)},
            )

        return Response(FamilySerializer(family, context={'request': request}).data)


@extend_schema(summary='Leave a family', tags=['Family'])
class LeaveFamilyView(APIView):
    def post(self, request, family_id):
        membership = get_object_or_404(
            FamilyMembership, family_id=family_id, user=request.user
        )

        if membership.role == FamilyMembership.Role.CREATOR:
            return Response(
                {'error': 'Creator cannot leave. Transfer ownership or delete the family.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        membership.delete()
        return Response({'message': 'Left the family.'})


@extend_schema(summary='Remove a family member', tags=['Family'])
class RemoveMemberView(APIView):
    def post(self, request, family_id, user_id):
        family = get_object_or_404(Family, id=family_id, created_by=request.user)
        membership = get_object_or_404(FamilyMembership, family_id=family_id, user_id=user_id)

        if membership.role == FamilyMembership.Role.CREATOR:
            return Response({'error': 'Cannot remove the family creator.'}, status=status.HTTP_400_BAD_REQUEST)

        membership.delete()
        return Response({'message': 'Member removed.'})


@extend_schema(summary='Update member role', tags=['Family'])
class UpdateMemberRoleView(APIView):
    def post(self, request, family_id):
        family = get_object_or_404(Family, id=family_id, created_by=request.user)
        serializer = UpdateMemberRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        membership = get_object_or_404(
            FamilyMembership, family_id=family_id, user_id=serializer.validated_data['user_id']
        )

        if membership.role == FamilyMembership.Role.CREATOR:
            return Response({'error': 'Cannot change creator role.'}, status=status.HTTP_400_BAD_REQUEST)

        membership.role = serializer.validated_data['role']
        membership.save(update_fields=['role'])

        return Response(FamilyMemberSerializer(membership).data)
