from django.db import models
# from django.contrib.auth import get_user_model
from django.conf import settings


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код',
        max_length=200,
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Еденица измерения',
        max_length=200,
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    title = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    # image = models.ImageField(
    # verbose_name='Изображение',
    # upload_to='recipes/',
    # null=True,
    # blank=True
    # )
    text = models.TextField(
        verbose_name='Описание',
    )
    # ingredients =
