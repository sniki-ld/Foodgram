from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для кастомной модели пользователя."""
    password = serializers.CharField()

    extra_kwargs = {'username': {'required': True},
                    'email': {'required': True},
                    'first_name': {'first_name': True},
                    'last_name': {'last_name': True},
                    'password': {'password': True}
                    }

    class Meta:
        fields = [
            'id',
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
        ]

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


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для конечной точки смены пароля."""
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    model = User