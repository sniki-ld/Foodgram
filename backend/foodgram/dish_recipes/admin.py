from django.contrib import admin

from .models import Tag, Ingredient, Recipe, IngredientAmount, Follow, Favorites, ShopList, RecipeTag


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
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    """Администрирование рецептов."""
    list_display = ('id', 'author', 'name', 'show_tags', 'cooking_time', 'show_ingredients', 'favorited_count')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', 'author', 'tags')
    ordering = ('name',)
    empty_value_display = '-пусто-'

    def show_ingredients(self, obj):
        return '\n'.join([item.ingredient.name for item in obj.ingredient.all()])

    show_ingredients.short_description = 'Ингредиенты в рецепте'

    def show_tags(self, obj):
        return '\n'.join([item.name for item in obj.tag.all()])

    show_tags.short_description = 'Тэги в рецепте'

    def favorited_count(self, obj):
        favorited_count = Favorites.objects.filter(recipe=obj).count()
        return favorited_count

    favorited_count.short_description = 'В избранном'


class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'amount')


class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag')


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
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Favorites, FavoritesAdmin)
admin.site.register(ShopList, ShopListAdmin)
