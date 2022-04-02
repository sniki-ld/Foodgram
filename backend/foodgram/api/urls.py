from rest_framework.routers import DefaultRouter
from django.urls import path, include, re_path
from .views import ChangePasswordView, UsersMeApiView

from .views import CustomUserViewSet

app_name = 'api'

router = DefaultRouter()

router.register('users', CustomUserViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('users/set_password/', ChangePasswordView.as_view()),
    path('users/me/', UsersMeApiView.as_view()),
    path('', include(router.urls))
]
