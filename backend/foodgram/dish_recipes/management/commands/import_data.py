from django.core.management.base import BaseCommand

from .parsers.model_parsers import ingredient_parser


class Command(BaseCommand):
    help = 'Импорт данных в БД из csv файлов.'

    HANDLERS = {
        'ingredient': ingredient_parser
    }

    def add_arguments(self, parser):
        parser.add_argument('--model', nargs='?', type=str, action='store')
        parser.add_argument('--file', nargs='?', type=str, action='store')

    def handle(self, *args, **options):
        Command.HANDLERS[options['model']](options['file'])
