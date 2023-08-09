from django.contrib.auth import get_user_model
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomObtainAuthToken, UserCreateView, UserViewSet

User = get_user_model()

router = DefaultRouter()
router.register('users', UserViewSet, basename='api-user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/registration/', UserCreateView.as_view(), name='api-register'),
    path('auth/verification/',
         CustomObtainAuthToken.as_view(),
         name='api-verification'),
]
