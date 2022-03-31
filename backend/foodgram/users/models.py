# Создаем свой UserManger и переопределяем методы, которые отвечают за создание пользователя:
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


# Создаем класс менеджера пользователей
class MyUserManager(BaseUserManager):
    """Создает и сохраняет пользователя с заданным username, email."""

    # Создаём базовый метод для создания пользователя
    def create_user(self, email, username, password=None, **extra_fields):
        # Проверяем есть ли Email
        if not email:
            raise ValueError('e-mail обязателен для регистрации!')

        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(
            username=username, email=email, **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Суперпользователь должен иметь is_admin=True.')

        return self.create_user(
            username, email, password, **extra_fields
        )


username_validator = UnicodeUsernameValidator()  # Letters, digits and @/./+/-/_ only.


class CustomUser(AbstractBaseUser):
    """Описываем кастомную модель пользователя."""
    email = models.EmailField(unique=True, max_length=254,
                              verbose_name='email')
    username = models.CharField(unique=True,
                                validators=[username_validator],
                                max_length=150,
                                verbose_name='имя пользователя')
    date_joined = models.DateTimeField(verbose_name='дата создания',
                                       auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='последний вход в систему',
                                      auto_now=True)

    is_active = models.BooleanField(default=True,
                                    verbose_name='активный')
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    first_name = models.CharField(max_length=150, blank=True,
                                  verbose_name='имя')
    last_name = models.CharField(max_length=150, blank=True,
                                 verbose_name='фамилия')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = MyUserManager()

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f'{self.first_name}  {self.last_name}'

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
