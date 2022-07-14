![workflow](https://github.com/sniki-ld/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

http://foodgram-ld.ddns.net/

http://foodgram-ld.ddns.net/admin/

## Foodgram
___
Проект Foodgram - это онлайн-сервис и API для него. 
На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Установка
Для установки на локальной машине потребуется:

- Клонировать репозиторий
- Установить и настроить Docker
---
### Создайте файл _.env_ с переменными окружения для работы с базой данных

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<db_name>
POSTGRES_USER=<postgres_user>
POSTGRES_PASSWORD=<postgres_password>
DB_HOST=db
DB_PORT=5432
```
---
### Запуск приложения
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
## Для репозитория настроен CI/CD.

### Для работы с удаленным сервером (на ubuntu):

1.Сделайте Fork данного репозитория

2.Подготовьте vps с ubuntu и docker

- Выполните вход на свой удаленный сервер
- Установите docker на сервер:
```
sudo apt install docker.io 
```
- Установите docker-compose на сервер:
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
- Локально отредактируйте файл infra/nginx.conf и в строке server_name впишите свой IP
- Скопируйте файлы _docker-compose.yaml_ и _nginx.conf_ из вашего проекта на сервер в _home/<ваш_username>/docker-compose.yaml_ и _home/<ваш_username>/nginx.conf_ соответственно.
```
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
```
- Cоздайте .env файл и впишите:
```
DB_ENGINE=<django.db.backends.postgresql>
DB_NAME=<имя базы данных postgres>
DB_USER=<пользователь бд>
DB_PASSWORD=<пароль>
DB_HOST=<db>
DB_PORT=<5432>
SECRET_KEY=<секретный ключ проекта django>
```
- Для работы с Workflow добавьте в Secrets GitHub переменные окружения для работы:
```
DB_ENGINE=<django.db.backends.postgresql>
DB_NAME=<имя базы данных postgres>
DB_USER=<пользователь бд>
DB_PASSWORD=<пароль>
DB_HOST=<db>
DB_PORT=<5432>

DOCKER_PASSWORD=<пароль от DockerHub>
DOCKER_USERNAME=<имя пользователя>

SECRET_KEY=<секретный ключ проекта django>

USER=<username для подключения к серверу>
HOST=<IP сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

TELEGRAM_TO=<ID чата, в который придет сообщение>
TELEGRAM_TOKEN=<токен вашего бота>
```
### Проверка работоспособности
Комманда `git push` является триггером workflow. 
После любого изменения в проекте и выполнения `git add . git commit -m "..." git push`
запустится последовательно цепочка команд:
- _собрать проект_
- _тестировать проект на соответствие PEP8_
- _собрать образ (image) для docker контейнера и отправить в DockerHub_
- _задеплоить проект на сервер_

**При необходимости можно подключиться к контейнеру:**
- Находим имя или ID контейнера:
```
docker ps
```
- Подключаемся:
```
docker exec -it <CONTAINER ID> bash
```
- Выход:
```
Ctrl+D
```
### Проект будет доступен по вашему IP
___
### Авторы
Елена Денисова - Разработала бэкенд и деплой для сервиса Foodgram.


Яндекс.Практикум - Фронтенд для сервиса Foodgram.




