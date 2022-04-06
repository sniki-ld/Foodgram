from rest_framework.authtoken.admin import User
from rest_framework.response import Response
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .pagination import CustomPagination
from .serializers import UserSerializer, TagSerializer, ChangePasswordSerializer, IngredientSerializer, \
    RecipeSerializer, FollowSerializer, FavoritesSerializer, ShopListSerializer
from users.models import User
from dish_recipes.models import Tag, Ingredient, Recipe, Follow, Favorites, ShopList


class UserViewSet(viewsets.ModelViewSet):
    """Сериализатор для модели пользователей."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]


class ChangePasswordView(generics.CreateAPIView):
    """Конечная точка для смены пароля."""
    serializer_class = ChangePasswordSerializer

    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Проверить старый пароль
            if not self.object.check_password(serializer.data.get("current_password")):
                return Response({"current_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password также хеширует пароль, который получит пользователь
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Пароль успешно обновлен',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersMeApiView(APIView):
    """Отдельно описываем поведение для users/me."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(self.request.user)
        return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    pagination_class = CustomPagination


class FavoritesViewSet(viewsets.ModelViewSet):
    queryset = Favorites.objects.all()
    serializer_class = FavoritesSerializer
    pagination_class = None


class ShopListViewSet(viewsets.ModelViewSet):
    queryset = ShopList.objects.all()
    serializer_class = ShopListSerializer
    pagination_class = None
