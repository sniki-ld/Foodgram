import django_filters
from django_filters import rest_framework as filters

from dish_recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    """Кастомный фильтр для модели Ingredient."""

    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Кастомный фильтр для модели Recipe."""

    tags = django_filters.AllValuesMultipleFilter(
        field_name='tag__slug'
    )
    author = django_filters.AllValuesFilter(
        field_name='author__id'
    )

    class Meta:
        model = Recipe
        fields = ('tag',)
