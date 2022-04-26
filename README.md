![workflow](https://github.com/sniki-ld/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

https://foodgram-ld.ddns.net//
https://foodgram-ld.ddns.net//admin/

Учетные данные superuser:
user: deni@ld.com password: 123
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
В контейнере backend выполнить миграции:
```
docker-compose exec backend python manage.py migrate
```
Создать суперпользователя
```
docker-compose exec backend python manage.py createsuperuser
```
Загружаем подготовленные данные для нашего приложения
```
docker-compose exec backend python3 manage.py loaddata fixtures.json
```
Приложение запущено и готово к использованию.

___
##Для репозитория настроен CI/CD.
**Для запуска приложения:**

1.Сделайте Fork данного репозитория

2.Подготовьте vps с ubuntu и docker

3.Добавьте action secrets под Ваш проект:
DB_ENGINE
DB_HOST
DB_NAME
DB_PORT
DOCKER_PASSWORD
DOCKER_USERNAME
HOST
PASSPHRASE
POSTGRES_DB
POSTGRES_PASSWORD
POSTGRES_USER
SECRET_KEY
SSH_KEY
USER
(пользователь на хосте)