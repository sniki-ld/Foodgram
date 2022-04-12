from django.contrib.auth import get_user_model
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator
# from users.models import User
from dish_recipes.models import Tag, Ingredient, IngredientAmount, FavoritesRecipe, Follow, ShopList, Recipe, RecipeTag

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""
    password = serializers.CharField()

    extra_kwargs = {'username': {'required': True},
                    'email': {'required': True},
                    'first_name': {'first_name': True},
                    'last_name': {'last_name': True},
                    'password': {'password': True}
                    }

    class Meta:
        fields = (
            'id',
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
        )

        model = User

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        return user


class UserShowSerializer(serializers.ModelSerializer):
    """Сериализатор модели пользователя для подписок."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj.id).exists()


class ChangePasswordSerializer(serializers.ModelSerializer):
    """Сериализатор для конечной смены пароля."""
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('current_password', 'new_password')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиентов."""

    class Meta:
        model = Ingredient
        fields = 'id', 'amount'


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
    """Сериализатор для вывода количества ингредиентов"""
    id = serializers.ReadOnlyField(source='tag.id')
    name = serializers.ReadOnlyField(source='tag.name')

    class Meta:
        model = RecipeTag
        fields = ('id', 'name')


class AddIngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('amount', 'id')


class RecipeAddSerializer(serializers.ModelSerializer):
    """
    Сериализатор вывода списка рецептов и
    получения определённого рецепта.
    """
    image = Base64ImageField()
    author = UserShowSerializer(read_only=True)
    tags = TagSerializer(source='tag', many=True, read_only=True)
    ingredients = IngredientAmountSerializer(source='ingredient', many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return FavoritesRecipe.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShopList.objects.filter(
            user=request.user, recipe=obj).exists()


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания, обновления и удаления рецептов.
    """
    image = Base64ImageField()
    author = UserShowSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, source='tag',
    )
    ingredients = AddIngredientAmountSerializer(many=True, source='ingredient')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'text',
                  'image', 'cooking_time')

    def validate(self, data):
        """Проверяем, создавал ли пользователь рецепт с таким же именем ранее."""
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
        print(ingredients_data)
        tags_data = validated_data.pop('tag')
        print(tags_data)
        recipe = Recipe.objects.create(image=image, **validated_data)

        for ingredient in ingredients_data:
            add_ingredient = IngredientAmount.objects.create(
                ingredient=ingredient['id'],
                amount=ingredient['amount']

            )
            recipe.ingredient.add(add_ingredient)
        recipe.tag.set(tags_data)
        return recipe

    def to_representation(self, instance):
        return RecipeAddSerializer(
            instance,
            context={"request": self.context.get("request")}).data

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredient')
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tag.clear()
        tags_data = self.initial_data.get('tags')
        instance.tag.set(tags_data)
        IngredientAmount.objects.filter(recipes=instance).delete()
        for ingredient in ingredients_data:
            add_ingredient = IngredientAmount.objects.create(
                ingredient=ingredient['id'],
                amount=ingredient['amount']

            )
            instance.ingredient.add(add_ingredient)
        instance.save()
        return instance


class FollowerRecipeSerializer(serializers.ModelSerializer):
    """Рецепт для подписки"""
    image = serializers.SerializerMethodField('image_url')

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def image_url(self, obj):
        return '/media/' + str(obj.image)


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели мои подписки."""
    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'author']
            )
        ]

    def validate(self, data):
        if self.context['request'].user != data.get('author'):
            return data
        raise serializers.ValidationError("Нельзя подписаться на самого себя")


class FollowerSerializer(serializers.ModelSerializer):
    """Подписаться"""
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
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if recipes_limit:
            queryset = queryset[:recipes_limit]

        serializer = FollowerRecipeSerializer(queryset, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class FavoritesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели избранного."""

    class Meta:
        model = FavoritesRecipe
        fields = ('user', 'recipe')


class ShopListSerializer(serializers.ModelSerializer):
    """Сериализатор для модели списка покупок."""

    class Meta:
        model = ShopList
        fields = ('user', 'recipe')
