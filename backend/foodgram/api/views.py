from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from dish_recipes.models import (FavoritesRecipe, Ingredient, IngredientAmount,
                                 Recipe, ShopList, Tag)

from .download_pdf import download_pdf
from .filters import IngredientFilter, RecipeFilter
from .mixins import ListRetrieveCreateViewSet, ListRetrieveViewSet
from .pagination import CustomPagination
from .serializers import (ChangePasswordSerializer, FollowerRecipeSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeReadOnlySerializer, RecipeSerializer,
                          SubscriptionsSerializer, TagSerializer,
                          UserSerializer)

User = get_user_model()


class UserViewSet(ListRetrieveCreateViewSet):
    """Представление для эндпоинта users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    @action(['post'], detail=False, permission_classes=(IsAuthenticated,))
    def set_password(self, request, *args, **kwargs):
        """Представление для эндпоинта смены пароля пользователя."""
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not self.request.user.check_password(
                serializer.data.get("current_password")):
            return Response({"current_password": ["Неверный пароль!"]},
                            status=status.HTTP_400_BAD_REQUEST)
        self.request.user.set_password(
            serializer.validated_data['new_password']
        )
        self.request.user.save()
        response = {
            'status': 'success',
            'code': status.HTTP_204_NO_CONTENT,
            'message': 'Пароль успешно обновлен!',
        }

        return Response(response)

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated])
    def me(self, request):
        """Представление для эндпоинта 'текущий пользователь'."""
        serializer = UserSerializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Выводим все подписки."""
        queryset = self.request.user.follower.all()
        if not queryset.exists():
            return Response('Вы еще ни на кого не подписаны',
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
        """Подписываемся на пользователя."""
        user = self.request.user
        author = get_object_or_404(User, id=self.kwargs["pk"])
        data = {'user': user.id, 'author': author.id}
        serializer = FollowSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, requests, **kwargs):
        """Удаляем подписку."""
        author = get_object_or_404(User, id=self.kwargs["pk"])
        subscription = self.request.user.follower.filter(
            author=author).delete()
        if not subscription:
            return Response({
                'errors': 'У вас нет подписки на данного автора!'},
                          status=status.HTTP_400_BAD_REQUEST)
        return Response('Подписка удалена!',
                        status=status.HTTP_204_NO_CONTENT)


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
    """Представление для работы с рецептами."""
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    serializer_class = RecipeSerializer
    permission_classes = [AllowAny]
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
        """Добавляем рецепт в избранное."""
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
        serializer = FollowerRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, **kwargs):
        """Удаляем рецепт из избранного."""
        recipe = get_object_or_404(Recipe, id=self.kwargs["pk"])
        favorite = FavoritesRecipe.objects.filter(
            user=self.request.user, recipe=recipe).delete()
        if not favorite:
            return Response({'errors': 'У вас нет такого рецепта!'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response('Рецепт удален из избранного!',
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        """Добавляем рецепт в список покупок."""
        recipe = get_object_or_404(Recipe, id=self.kwargs["pk"])
        user = self.request.user
        cart, created = ShopList.objects.get_or_create(
            user=user,
            recipe=recipe
        )
        if not created:
            return Response({'errors': 'Данный рецепт уже в списке покупок!'},
                            status=status.HTTP_400_BAD_REQUEST
                            )
        serializer = FollowerRecipeSerializer(recipe)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, **kwargs):
        """Удаляем рецепт из списка покупок."""
        recipe = get_object_or_404(Recipe,
                                   id=self.kwargs["pk"])
        shop_list = ShopList.objects.filter(user=self.request.user,
                                            recipe=recipe).delete()
        if not shop_list:
            return Response({'errors': 'В вашем списке'
                                       ' покупок нет такого рецепта!'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response('Рецепт удален из списка покупок!',
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """
        Формируем список продуктов для покупки и
        возвращаем его в виде pdf-файла.
        """
        user = self.request.user
        recipe_id = user.user_shop_lists.filter(user=user).values_list(
            'recipe_id', flat=True)
        ingredients = IngredientAmount.objects.values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(count=Sum('amount')).filter(recipes__id__in=recipe_id)
        shopping_list = []
        for ingredient in ingredients:
            shopping_list.append(
                f"{ingredient['ingredient__name']} -- "
                f"{ingredient['count']} "
                f"{ingredient['ingredient__measurement_unit']}")

        buffer = download_pdf(shopping_list)
        return FileResponse(buffer, as_attachment=True, filename='BuyList.pdf')
