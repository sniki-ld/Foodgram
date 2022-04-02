from rest_framework import serializers
from users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для кастомной модели пользователя."""
    password = serializers.CharField()

    extra_kwargs = {'username': {'required': True},
                    'email': {'required': True},
                    'first_name': {'first_name': True},
                    'last_name': {'last_name': True},
                    'password': {'password': True}
                    }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user

    class Meta:
        fields = [
            'id',
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
        ]
        model = CustomUser


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для конечной точки смены пароля."""
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    model = CustomUser
