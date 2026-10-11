from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views

urlpatterns = [
    # Authentication
    path('auth/register/', views.UserRegistrationView.as_view(), name='auth-register'),
    path('auth/login/', views.LoginView.as_view(), name='auth-login'),
    path('auth/otp/request/', views.RequestOTPView.as_view(), name='auth-otp-request'),
    path('auth/otp/verify/', views.VerifyOTPView.as_view(), name='auth-otp-verify'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token-verify'),

    # Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile-update'),
    path('profile/privacy/', views.PrivacySettingsUpdateView.as_view(), name='profile-privacy'),
    path('profile/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('profile/fcm-token/', views.UpdateFCMTokenView.as_view(), name='fcm-token-update'),
    path('profile/fcm-token/remove/', views.RemoveFCMTokenView.as_view(), name='fcm-token-remove'),

    # Emergency Contacts
    path('emergency-contacts/', views.EmergencyContactListView.as_view(), name='emergency-contacts'),
    path('emergency-contacts/<int:pk>/', views.EmergencyContactDetailView.as_view(), name='emergency-contact-detail'),

    # Users
    path('users/search/', views.UserSearchView.as_view(), name='users-search'),

    # Admin: User Management
    path('admin/users/', views.AdminUserListView.as_view(), name='admin-users'),
    path('admin/users/<uuid:user_id>/', views.AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/users/<uuid:user_id>/role/', views.AdminUpdateRoleView.as_view(), name='admin-user-role'),
    path('admin/users/<uuid:user_id>/block/', views.AdminBlockUserView.as_view(), name='admin-user-block'),
    path('admin/sos/', views.AdminSOSListView.as_view(), name='admin-sos-list'),
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
]
