from django.urls import path
from .views import LandingContentView, AssetView
urlpatterns = [path('content/', LandingContentView.as_view(), name='landing-content'), path('content/files/<int:pk>/', AssetView.as_view(), name='landing-file')]
