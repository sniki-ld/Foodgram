from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Описываем кастомную модель пользователя."""
    email = models.EmailField(unique=True, max_length=254,
                              verbose_name='email')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f'{self.first_name}  {self.last_name}'

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
