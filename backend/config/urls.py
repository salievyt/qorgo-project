from django.urls import include, path
from rest_framework.routers import DefaultRouter
from safety import views
router = DefaultRouter()
router.register('contacts', views.ContactViewSet, basename='contacts')
router.register('alerts', views.AlertViewSet, basename='alerts')
router.register('journeys', views.JourneyViewSet, basename='journeys')
urlpatterns = [
    path('api/register/', views.register), path('api/login/', views.login),
    path('api/logout/', views.logout), path('api/profile/', views.profile),
    path('api/capabilities/', views.capabilities), path('api/', include(router.urls)),
]
