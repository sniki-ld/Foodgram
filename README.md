## Foodgram
___
Проект Foodgram - это онлайн-сервис и API для него. 
На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Установка
Для установки на локальной машине потребуется:

- Клонировать репозиторий
- Установить и настроить Docker
---
## Создайте файл _.env_ с переменными окружения для работы с базой данных

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<db_name>
POSTGRES_USER=<postgres_user>
POSTGRES_PASSWORD=<postgres_password>
DB_HOST=db
DB_PORT=5432
```
---
## Запуск приложения
Перейти в директорию с проектом в папку с файлом docker-compose.yaml
Собрать контейнеры и запустить их
```
docker-compose up -d --build
```
В контейнере web выполнить миграции:
```
docker-compose exec web python manage.py migrate
```
Создать суперпользователя
```
docker-compose exec web python manage.py createsuperuser
```
Загружаем подготовленные данные для нашего приложения
```
docker-compose exec web python3 manage.py loaddata fixtures.json
```
Приложение запущено и готово к использованию.
