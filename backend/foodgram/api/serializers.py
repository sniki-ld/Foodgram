from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import User
from dish_recipes.models import Tag, Ingredient, IngredientAmount, Favorites, Follow, ShopList, Recipe


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""
    password = serializers.CharField()
    is_subscribed = serializers.SerializerMethodField()

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
            'is_subscribed'
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

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj.id).exists()


class ChangePasswordSerializer(serializers.ModelSerializer):
    """Сериализатор для конечной точки смены пароля."""
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
        fields = '__all__'


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


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели рецептов."""
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientAmountSerializer(source='ingredients_amounts', many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'name', 'text',
                  'image', 'ingredients', 'cooking_time', 'is_favorited', 'is_in_shopping_cart')
        # depth = 1

    def general_response(self, request_obj, general_obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return general_obj.objects.filter(user=request.user,
                                          recipe=request_obj.id).exists()

    def get_is_favorited(self, obj):
        return self.general_response(obj, Favorites)

    def get_is_in_shopping_cart(self, obj):
        return self.general_response(obj, ShopList)


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели подписки."""
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

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


class FavoritesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели избранного."""

    class Meta:
        model = Favorites
        fields = ('user', 'recipe')


class ShopListSerializer(serializers.ModelSerializer):
    """Сериализатор для модели списка покупок."""

    class Meta:
        model = ShopList
        fields = ('user', 'recipe')
