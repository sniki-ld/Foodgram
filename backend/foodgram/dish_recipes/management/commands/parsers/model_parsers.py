import csv
import os

from django.conf import settings

from dish_recipes.models import Ingredient


def csv_parser(file):
    """Функционал для csv."""
    file_path = os.path.join(settings.BASE_DIR, file)
    result = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            result.append(row)
    return result


def ingredient_parser(file):
    """Парсер для модели ингредиентов."""
    rows = csv_parser(file)
    objs = [
        Ingredient(
            name=row[0],
            measurement_unit=row[1],
        )
        for row in rows
    ]
    Ingredient.objects.bulk_create(objs)
