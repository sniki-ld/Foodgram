from rest_framework.routers import DefaultRouter
from django.urls import path, include, re_path

from .views import UserViewSet, UsersMeApiView

app_name = 'api'

router = DefaultRouter()

router.register('users', UserViewSet)

urlpatterns = [
    path(r'auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('users/me/', UsersMeApiView.as_view()),
    path('', include(router.urls))
]
