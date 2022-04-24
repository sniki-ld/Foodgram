from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField, PrimaryKeyRelatedField
from rest_framework.validators import UniqueTogetherValidator

from dish_recipes.models import (FavoritesRecipe, Follow, Ingredient,
                                 IngredientAmount, Recipe, RecipeTag, ShopList,
                                 Tag)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""
    password = serializers.CharField(write_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'id',
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
            'is_subscribed'
        )

        extra_kwargs = {'username': {'required': True},
                        'email': {'required': True},
                        'first_name': {'required': True},
                        'last_name': {'required': True},
                        'password': {'required': True}
                        }

        model = User

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (bool(request) and
                request.user.is_authenticated and
                request.user.follower.filter(author=obj.id).exists())


class ChangePasswordSerializer(serializers.ModelSerializer):
    """Сериализатор смены пароля для модели пользователя."""
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('current_password', 'new_password')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода количества ингредиентов"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeTagSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления тегов в рецепт."""
    id = serializers.ReadOnlyField(source='tag.id')
    name = serializers.ReadOnlyField(source='tag.name')

    class Meta:
        model = RecipeTag
        fields = ('id', 'name')


class AddIngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов в рецепт."""
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        fields = ('id', 'amount')
        model = IngredientAmount


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""
    image = serializers.SerializerMethodField('image_url')
    author = UserSerializer(read_only=True)
    tags = TagSerializer(source='tag', many=True, read_only=True)
    ingredients = IngredientAmountSerializer(
        source='ingredient', many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (bool(request) and
                request.user.is_authenticated and
                FavoritesRecipe.objects.filter(
            user=request.user, recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (bool(request) and
                request.user.is_authenticated and
                ShopList.objects.filter(
            user=request.user, recipe=obj).exists())

    def image_url(self, obj):
        return '/media/' + str(obj.image)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания, обновления и удаления рецептов."""
    image = Base64ImageField()
    author = SlugRelatedField(slug_field='username',
                              default=serializers.CurrentUserDefault(),
                              read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, source='tag',
    )
    ingredients = AddIngredientAmountSerializer(
        many=True, source='ingredient')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name',
                  'text', 'image', 'cooking_time')

    def validate(self, data):
        """
        Проверяем, создавал ли пользователь рецепт
        с таким же именем ранее.
        """
        request = self.context['request']
        recipe_name = data.get('name')
        author = request.user
        if (Recipe.objects.filter(author=author,
                                  name=recipe_name).exists()
                and request.method != 'PATCH'):
            raise serializers.ValidationError(
                'Такой рецепт у вас уже есть!'
            )
        return data

    def create(self, validated_data):
        image = validated_data.pop('image')
        ingredients_data = validated_data.pop('ingredient')
        tags_data = validated_data.pop('tag')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tag.set(tags_data)
        for ingredient in ingredients_data:
            add_ingredient = IngredientAmount.objects.create(
                ingredient=ingredient['id'],
                amount=ingredient['amount'])
            recipe.ingredient.add(add_ingredient)
        return recipe

    def to_representation(self, instance):
        return RecipeReadOnlySerializer(
            instance,
            context={"request": self.context.get("request")}).data

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredient')
        tags_data = validated_data.pop('tag')
        super().update(instance, validated_data)
        IngredientAmount.objects.filter(recipes=instance).delete()
        recipe = instance
        for ingredient in ingredients_data:
            ing = IngredientAmount.objects.create(
                ingredient=ingredient['id'],
                amount=ingredient['amount'])
            recipe.ingredient.add(ing)

        instance.tag.set(tags_data)
        return recipe


class FollowerRecipeSerializer(serializers.ModelSerializer):
    """Вспомогательный сериализатор для рецептов в подписках."""
    image = serializers.SerializerMethodField('image_url')

    def image_url(self, obj):
        return '/media/' + str(obj.image)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода всех подписок."""
    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'author'],
                message='Вы уже подписаны на этого автора!'
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        author = data['author']
        if request.user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя!')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscriptionsSerializer(instance, context=context).data


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки на пользователя."""
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (bool(request) and
                request.user.is_authenticated and
                Follow.objects.filter(
            user=obj.user, author=obj.author).exists())

    def get_recipes(self, obj):
        params = self.context.get("request").query_params
        limit = params.get('recipes_limit')
        recipes = obj.author.recipes
        if limit:
            recipes = recipes.all()[:int(limit)]
        context = {'request': self.context.get("request")}
        return FollowerRecipeSerializer(
            recipes, context=context, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class FavoritesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели избранного."""

    class Meta:
        model = FavoritesRecipe
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FollowerRecipeSerializer(
            instance.recipe, context=context).data


class ShopListSerializer(serializers.ModelSerializer):
    """Сериализатор для модели списка покупок."""

    class Meta(FavoritesSerializer.Meta):
        model = ShopList

    def validate(self, data):
        request = self.context.get('request')
        recipe_id = data['recipe'].id
        purchase_exists = ShopList.objects.filter(
            user=request.user,
            recipe__id=recipe_id
        ).exists()

        if request.method == 'GET' and purchase_exists:
            raise serializers.ValidationError(
                'Рецепт уже в списке покупок')

        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FollowerRecipeSerializer(
            instance.recipe, context=context).data
