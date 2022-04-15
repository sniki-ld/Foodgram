import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.authtoken.admin import User
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from dish_recipes.models import (FavoritesRecipe, Follow, Ingredient,
                                 IngredientAmount, Recipe, ShopList, Tag)

from .filters import IngredientFilter, RecipeFilter
from .mixins import ListRetrieveCreateViewSet, ListRetrieveViewSet
from .pagination import CustomPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (ChangePasswordSerializer, FollowerRecipeSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeReadOnlySerializer, RecipeSerializer,
                          SubscriptionsSerializer, TagSerializer,
                          UserSerializer)


class UserViewSet(ListRetrieveCreateViewSet):
    """Представление для эндпоинта users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    @action(['post'], detail=False, permission_classes=(IsAuthenticated,))
    def set_password(self, request, *args, **kwargs):
        """Представление для эндпоинта смены пароля пользователя."""
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not self.request.user.check_password(
                    serializer.data.get("current_password")):
                return Response({"current_password": ["Неверный пароль!"]},
                                status=status.HTTP_400_BAD_REQUEST)
            self.request.user.set_password(
                serializer.validated_data['new_password']
            )
            self.request.user.save()
            response = {
                'message': 'Пароль успешно обновлен!',
            }

            return Response(response)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated])
    def me(self, request):
        """Представление для эндпоинта 'текущий пользователь'."""
        serializer = UserSerializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Вывод всех подписок."""
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

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        """Подписка на пользователя."""
        user = self.request.user
        author = get_object_or_404(User, id=self.kwargs["pk"])

        if user == author:
            return Response({
                'errors': 'Вы не можете подписаться на самого себя!'
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
        """Отписаится от пользователя."""
        author = get_object_or_404(User, id=self.kwargs["pk"])
        subscription = get_object_or_404(
            Follow,
            user=self.request.user,
            author=author)
        subscription.delete()
        return Response('Подписка удалена!', status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ListRetrieveViewSet):
    """Представление для эндпоинта Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ListRetrieveViewSet):
    """Представление для эндпоинта Ingredient."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с рецептами."""
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    serializer_class = RecipeSerializer
    permission_classes = [IsOwnerOrReadOnly, ]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tags', 'author',)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        """Переопределяем сохранение автора рецепта."""
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Определяем сериализаторы в зависимости от реквест методов."""
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeSerializer
        return RecipeReadOnlySerializer

    def get_queryset(self):
        """Фильтруем выборку рецептов, в зависимости от Query Params."""

        if self.request.query_params.get('is_favorited') == '1':
            user = self.request.user
            favorites = FavoritesRecipe.objects.filter(
                user=user
            ).values_list('recipe__id', flat=True)
            queryset = Recipe.objects.filter(id__in=favorites)
            return queryset
        if self.request.query_params.get('is_in_shopping_cart') == '1':
            user = self.request.user
            in_cart = ShopList.objects.filter(
                user=user
            ).values_list('recipe__id', flat=True)
            queryset = Recipe.objects.filter(id__in=in_cart)
            return queryset
        return Recipe.objects.all()

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
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
        favorite = get_object_or_404(FavoritesRecipe,
                                     user=self.request.user,
                                     recipe=recipe)
        favorite.delete()
        return Response('Рецепт удален из избранного!',
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
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
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs["pk"])
        cart = get_object_or_404(ShopList, user=self.request.user,
                                 recipe=recipe)
        cart.delete()
        return Response('Рецепт удален из списка покупок!',
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = self.request.user
        shopping_cart = user.user_shop_lists.all()
        purchase = {}
        for item in shopping_cart:
            recipe = item.recipe
            ingredients = IngredientAmount.objects.filter(recipes=recipe)
            for ingredient in ingredients:
                amount = ingredient.amount
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                if name not in purchase:
                    purchase[name] = {
                        'measurement_unit': measurement_unit,
                        'amount': amount
                    }
                else:
                    purchase[name]['amount'] = (
                            purchase[name]['amount'] + amount
                    )

        shopping_list = ([f'{item} - {purchase[item]["amount"]}'
                          f'{purchase[item]["measurement_unit"]} \n'
                          for item, value in purchase.items()])
        today = datetime.date.today()
        shopping_list.append(f'\n From FoodGram: Приятных покупок!\n {today}')
        response = HttpResponse(shopping_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="BuyList.txt"'
        return response
