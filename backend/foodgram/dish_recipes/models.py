from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    """Модель, представляющая тэги для фильтрации рецептов."""
    name = models.CharField(
        verbose_name='название',
        max_length=200,
        unique=True,
        help_text='Введите имя тега'
    )
    slug = models.SlugField(
        verbose_name='slag',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name='цвет',
        max_length=200,
        unique=True,
        help_text='Цветовой HEX-код'
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель, представляющая ингредиент (продукт) и его единицы измерения."""
    name = models.CharField(
        verbose_name='название',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='единица измерения',
        max_length=200,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class IngredientAmount(models.Model):
    """Модель для связи рецептов и ингредиентов."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ингредиент',
        related_name='ingredients_amounts',
    )
    amount = models.PositiveIntegerField(
        verbose_name='количество ингредиента',
    )

    class Meta:
        verbose_name = 'количество ингредиента в рецепте'
        verbose_name_plural = 'количество ингредиентов в рецепте'


class Recipe(models.Model):
    """Модель, представляющая рецепт."""
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        verbose_name='название',
        max_length=200,
        help_text='Введите название рецепта'
    )
    text = models.TextField(
        verbose_name='описание рецепта',
    )
    image = models.ImageField(
        verbose_name='изображение',
        upload_to='recipes/',
    )
    ingredient = models.ManyToManyField(
        IngredientAmount,
        related_name='recipes',
        verbose_name='ингредиенты',
    )
    tag = models.ManyToManyField(
        Tag,
        related_name='recipes',
        through='RecipeTag',
        verbose_name='теги',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='время приготовления',
        validators=[MinValueValidator(1, 'Значение не может быть меньше 1')]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'pецепт'
        verbose_name_plural = 'pецепты'

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """Модель для связи рецептов и тегов."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name='рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='тэг'
    )


class Follow(models.Model):
    """Модель, представляющая подписки."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'


class Favorites(models.Model):
    """Модель, представляющая избранные рецепты."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='favorite_user_recept_unique'
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у {self.user}'


class ShopList(models.Model):
    """Модель для добавления рецепта в список покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shop_lists',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_shop_lists',
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='purchase_user_recipe_unique'
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в списке покупок {self.user}'
