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

from .pagination import CustomPagination
from .serializers import UserSerializer, TagSerializer, ChangePasswordSerializer, IngredientSerializer, \
    RecipeSerializer, FollowSerializer, FavoritesSerializer, ShopListSerializer, RecipeAddSerializer, \
    UserShowSerializer, FollowerSerializer
from users.models import User
from dish_recipes.models import Tag, Ingredient, Recipe, Follow, FavoritesRecipe, ShopList


class UserViewSet(viewsets.ModelViewSet):
    """Сериализатор для модели пользователей."""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # pagination_class = CustomPagination
    # permission_classes = [AllowAny]

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

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = self.request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowerSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        user = self.request.user
        author = get_object_or_404(User, id=self.kwargs["pk"])
        if author == user:
            return Response(
                'Нельзя подписываться на самого себя!',
                status=status.HTTP_400_BAD_REQUEST)

        subscribe, created = Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
        if not created:
            return Response(
                'Вы уже подписаны на данного автора!',
                status=status.HTTP_400_BAD_REQUEST)
        subscribe.save()
        serializer = FollowerSerializer(author)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=self.kwargs["pk"])
        subscribe = get_object_or_404(
            Follow, user=self.request.user, author=author
        )
        subscribe.delete()

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


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с рецептами."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return RecipeSerializer
        return RecipeAddSerializer


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return user.follower.all()

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        recipes_limit = self.request.query_params.get('recipes_limit')
        if recipes_limit and recipes_limit.isnumeric():
            context['recipes_limit'] = int(
                self.request.query_params.get('recipes_limit'))
        return context


class FavoritesViewSet(viewsets.ModelViewSet):
    queryset = FavoritesRecipe.objects.all()
    serializer_class = FavoritesSerializer
    pagination_class = None


class ShopListViewSet(viewsets.ModelViewSet):
    queryset = ShopList.objects.all()
    serializer_class = ShopListSerializer
    pagination_class = None
