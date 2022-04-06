from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Tag, Ingredient, Recipe, IngredientAmount, Follow, Favorites, ShopList


class TagAdmin(admin.ModelAdmin):
    """Администрирование тегов."""
    list_display = ('id', 'name', 'slug', 'color')
    list_filter = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',), }
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    """Администрирование ингредиентов."""
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('^name',)
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    """Администрирование рецептов."""
    list_display = ('id', 'author', 'name', 'cooking_time', 'show_ingredients', 'preview', 'favorited_count')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name',)
    ordering = ('name',)
    empty_value_display = '-пусто-'

    readonly_fields = ['preview']

    def preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" style="max-height: 95px;>')

    def show_ingredients(self, obj):
        return '\n'.join([item.name for item in obj.ingredients.all()])

    def favorited_count(self, obj):
        favorited_count = Favorites.objects.filter(recipe=obj).count()
        return favorited_count


class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


class FollowAdmin(admin.ModelAdmin):
    """Администрирование подписки."""
    list_display = ('author', 'user')


class FavoritesAdmin(admin.ModelAdmin):
    """Администрирование избранного."""
    list_display = ('user', 'recipe')


class ShopListAdmin(admin.ModelAdmin):
    """Администрирование списка покупок."""
    list_display = ('user', 'recipe')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Favorites, FavoritesAdmin)
admin.site.register(ShopList, ShopListAdmin)
