# Generated by Django 2.2.19 on 2022-04-12 13:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dish_recipes', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='shoplist',
            name='purchase_user_recipe_unique',
        ),
        migrations.AlterField(
            model_name='favorites',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_recipe', to='dish_recipes.Recipe', verbose_name='рецепт'),
        ),
        migrations.AlterField(
            model_name='favorites',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_user', to=settings.AUTH_USER_MODEL, verbose_name='автор'),
        ),
        migrations.AlterField(
            model_name='follow',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='подписан на'),
        ),
        migrations.AlterField(
            model_name='follow',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower', to=settings.AUTH_USER_MODEL, verbose_name='подписчик'),
        ),
        migrations.AlterField(
            model_name='shoplist',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_shop_lists', to='dish_recipes.Recipe', verbose_name='рецепт'),
        ),
        migrations.AlterField(
            model_name='shoplist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_shop_lists', to=settings.AUTH_USER_MODEL, verbose_name='автор'),
        ),
        migrations.AddConstraint(
            model_name='shoplist',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_recipe_cart'),
        ),
    ]
