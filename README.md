![Django-app workflow](https://github.com/needred/foodgram-project-react/actions/workflows/backend.yml/badge.svg)

# Foodgram - «Продуктовый помощник» 
Благодаря данному сервису вы сможете сохранять рецепты, смотреть рецепты других пользователей, добавлять рецепты в избранное и создавать списки придокутов перед походом в магазин.


### Workflow
* test - Тестирование проекта по flake8
* build_and_push_to_docker_hub - Сборка и доставка докер-образов на Docker Hub
* deploy - Деплой проекта на боевой сервер.
* send_message_success - Отправка уведомления в Telegram

В репозиторий добавьте данные в **`Actions secrets`**:
- ```HOST``` - адрес сервера
- ```USER``` - пользователя
- ```SSH_KEY``` - приватный ssh ключ
- ```PASSPHRASE``` - кодовая фраза для ssh-ключа
- ```DOCKER_USERNAME``` - имя пользователя в DockerHub
- ```DOCKER_PASSWORD``` - пароль пользователя в DockerHub
- ```DB_ENGINE``` - django.db.backends.postgresql
- ```DB_NAME``` - postgres (по умолчанию)
- ```POSTGRES_USER``` - postgres (по умолчанию)
- ```POSTGRES_PASSWORD``` - postgres (по умолчанию)
- ```DB_HOST``` - db
- ```DB_PORT``` - 5432
- ```SECRET_KEY``` - секретный ключ приложения django
- ```TELEGRAM_TO``` - id своего телеграм-аккаунта
- ```TELEGRAM_TOKEN``` - токен бота

## Как развернуть проект на сервере:
Установите соединение с сервером:
```
ssh username@server_address
```
Обновите индекс пакетов APT:
```
sudo apt update
```
Обновите установленные в системе пакеты и установите обновления безопасности:
```
sudo apt upgrade -y
```
 
Скопируйте файлы `docker-compose.yml` и `nginx.conf` из вашего проекта на сервер:
```
scp docker-compose.yaml <username>@<host>/home/<username>/docker-compose.yaml
scp nginx.conf <username>@<host>/home/<username>/
```
Установите Docker и Docker-compose:
```
sudo apt install docker.io
```
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
```
sudo chmod +x /usr/local/bin/docker-compose
```
Проверьте корректность установки Docker-compose:
```
sudo  docker-compose --version
```

### После успешного деплоя:
Соберите статические файлы (статику):
```
sudo docker-compose exec backend python manage.py collectstatic --no-input
```
Примените миграции:
```
sudo docker-compose exec backend python manage.py makemigrations users
sudo docker-compose exec backend python manage.py makemigrations recipes
```
```
sudo docker-compose exec backend python manage.py migrate --noinput
```
Создайте суперпользователя:
```
sudo docker-compose exec backend python manage.py createsuperuser
```
При необходимости наполните базу тестовыми данными:
```
sudo docker-compose exec backend python manage.py load_ingredients
```
и
```
sudo docker-compose exec backend python manage.py load_tags
```

### Тестовые пользователи
Логин: ```admin1``` (суперюзер)  
Email: ```admin1@yandex.ru```  
Пароль: ```qwerty123```  

Логин: ```tim1```  
Email: ```tim1@yandex.ru```  
Пароль: ```qwerty123```  

Логин: ```tim2```  
Email: ```tim2@yandex.ru```  
Пароль: ```qwerty123```


## Ссылки
### Документация API Foodgram:
http://158.160.66.170/api/docs/redoc.html
### Развёрнутый проект:
http://158.160.66.170 
http://158.160.66.170/admin/

