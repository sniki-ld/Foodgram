from rest_framework.routers import DefaultRouter
from django.urls import path, include, re_path

from .views import UserViewSet, TagViewSet, IngredientViewSet, RecipeViewSet

app_name = 'api'

router = DefaultRouter()

router.register(r'users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')



urlpatterns = [
    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
