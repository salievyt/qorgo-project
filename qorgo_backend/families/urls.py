from django.urls import path
from . import views

urlpatterns = [
    path('families/', views.UserFamiliesView.as_view(), name='families-list'),
    path('families/create/', views.CreateFamilyView.as_view(), name='families-create'),
    path('families/join/', views.JoinFamilyView.as_view(), name='families-join'),
    path('families/<uuid:pk>/', views.FamilyDetailView.as_view(), name='families-detail'),
    path('families/<uuid:family_id>/leave/', views.LeaveFamilyView.as_view(), name='families-leave'),
    path('families/<uuid:family_id>/remove/<uuid:user_id>/', views.RemoveMemberView.as_view(), name='families-remove'),
    path('families/<uuid:family_id>/update-role/', views.UpdateMemberRoleView.as_view(), name='families-update-role'),
]
