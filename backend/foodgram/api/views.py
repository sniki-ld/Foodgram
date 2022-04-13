from django.shortcuts import get_object_or_404
from rest_framework.authtoken.admin import User
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .serializers import UserSerializer, TagSerializer, ChangePasswordSerializer, IngredientSerializer, \
    RecipeSerializer, FollowSerializer, RecipeAddSerializer, UserShowSerializer, SubscriptionsSerializer, \
    FavoritesSerializer, FollowerRecipeSerializer, IngredientAmountSerializer
from users.models import User
from dish_recipes.models import Tag, Ingredient, Recipe, Follow, FavoritesRecipe, ShopList, IngredientAmount


class UserViewSet(viewsets.ModelViewSet):
    """Сериализатор для модели пользователей."""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    pagination_class = CustomPagination
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserSerializer
        return UserShowSerializer

    @action(['post'], detail=False, permission_classes=(IsAuthenticated,))
    def set_password(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            # Проверить старый пароль
            if not self.request.user.check_password(serializer.data.get("current_password")):
                return Response({"current_password": ["Неверный пароль."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password также хеширует пароль, который получит пользователь
            self.request.user.set_password(
                serializer.validated_data['new_password']
            )
            self.request.user.save()
            response = {
                'message': 'Пароль успешно обновлен',
            }

            return Response(response)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=self.request.user)
        if not queryset.exists():
            return Response({'error': 'Вы еще ни на кого не подписаны'},
                            status=status.HTTP_400_BAD_REQUEST)

        page = self.paginate_queryset(queryset)
        if page:
            serializer = SubscriptionsSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionsSerializer(queryset, many=True,
                                             context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        user = self.request.user
        author = get_object_or_404(User, id=self.kwargs["pk"])

        if user == author:
            return Response({
                'errors': 'Вы не можете подписываться на самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)

        if Follow.objects.filter(user=user, author=author).exists():
            return Response({
                'errors': 'Вы уже подписаны на данного пользователя!'
            }, status=status.HTTP_400_BAD_REQUEST)

        data = {'user': user.id, 'author': author.id}
        serializer = FollowSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, requests, **kwargs):
        author = get_object_or_404(User, id=self.kwargs["pk"])
        subscription = get_object_or_404(
            Follow,
            user=self.request.user,
            author=author)
        subscription.delete()
        return Response('Подписка удалена!', status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserShowSerializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
    filterset_class = IngredientFilter
    # queryset = IngredientAmount.objects.all()
    # serializer_class = IngredientAmountSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с рецептами."""
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    serializer_class = RecipeAddSerializer
    permission_classes = [AllowAny]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tags', 'author',)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        """Переопределяем сохранение автора рецепта."""
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Определяем сериализаторы в зависимости от реквест методов."""
        if self.action == 'create' or self.action == 'update':
            return RecipeSerializer
        return RecipeAddSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs["pk"])
        user = self.request.user
        favorite, created = FavoritesRecipe.objects.get_or_create(
            user=user,
            recipe=recipe
        )
        if not created:
            return Response('Данный рецепт уже в избранном!',
                            status=status.HTTP_400_BAD_REQUEST
                            )
        favorite.save()
        serializer = FollowerRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs["pk"])
        favorite = get_object_or_404(FavoritesRecipe, user=self.request.user,
                                     recipe=recipe)
        favorite.delete()
        return Response('Рецепт удален из избранного!', status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs["pk"])
        user = self.request.user
        cart, created = ShopList.objects.get_or_create(
            user=user,
            recipe=recipe
        )
        if not created:
            return Response('Данный рецепт уже в корзине!',
                            status=status.HTTP_400_BAD_REQUEST
                            )
        cart.save()
        serializer = FollowerRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs["pk"])
        cart = get_object_or_404(ShopList, user=self.request.user,
                                 recipe=recipe)
        cart.delete()
        return Response('Рецепт удален из списка покупок!', status=status.HTTP_204_NO_CONTENT)

# class FollowViewSet(viewsets.ModelViewSet):
#     serializer_class = FollowSerializer
#     pagination_class = CustomPagination
#
#     def get_queryset(self):
#         user = self.request.user
#         return user.follower.all()
#
#     def perform_create(self, serializer):
#         return serializer.save(user=self.request.user)
#
#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         recipes_limit = self.request.query_params.get('recipes_limit')
#         if recipes_limit and recipes_limit.isnumeric():
#             context['recipes_limit'] = int(
#                 self.request.query_params.get('recipes_limit'))
#         return context
