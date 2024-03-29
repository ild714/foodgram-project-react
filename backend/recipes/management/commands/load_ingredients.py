from csv import reader

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Добавление ингредиентов из файла CSV.
    Запуск по команде:
    python manage.py load_ingredients локально
    sudo docker-compose exec backend python manage.py load_ingredients
    на удаленном сервере.
    Создает записи в модели Ingredients из списка.
    """
    help = 'Load ingredients data from csv-file to DB.'

    def handle(self, *args, **kwargs):
        with open(
                'recipes/data/ingredients.csv', 'r',
                encoding='UTF-8'
        ) as ingredients:
            for row in reader(ingredients):
                if len(row) == 2:
                    Ingredient.objects.get_or_create(
                        name=row[0], measurement_unit=row[1],
                    )
