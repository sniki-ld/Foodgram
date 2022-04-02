from rest_framework.authtoken.admin import User
from rest_framework.response import Response
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics
from .serializers import ChangePasswordSerializer
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer
from users.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class ChangePasswordView(generics.CreateAPIView):
    """
    Конечная точка для смены пароля.
    """
    serializer_class = ChangePasswordSerializer
    model = User
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
        """Получаем себя при обращении на users/me."""
        serializer = UserSerializer(self.request.user)
        return Response(serializer.data)

