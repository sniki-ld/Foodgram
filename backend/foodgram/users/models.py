from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Описываем кастомную модель пользователя."""
    email = models.EmailField(unique=True, max_length=254,
                              verbose_name='email')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']

    @property
    def is_admin_or_superuser(self):
        """Описываем свойства для пермишенов."""
        return self.is_staff or self.is_superuser

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return True
