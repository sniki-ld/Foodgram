from rest_framework.routers import DefaultRouter
from django.urls import path, include, re_path

from .views import UserViewSet, UsersMeApiView, TagViewSet, IngredientViewSet, RecipeViewSet, FollowViewSet

app_name = 'api'

router = DefaultRouter()

router.register('users', UserViewSet)
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
# router.register('users/subscriptions/', FollowViewSet, basename='subscriptions')


urlpatterns = [
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('users/me/', UsersMeApiView.as_view()),
    # path('users/subscriptions/',FollowListView.as_view(),name='subscriptions'
    # ),
    path('', include(router.urls))
]
