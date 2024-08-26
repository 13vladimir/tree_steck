# Проект «Foodgram»
## Описание
![workflow](https://github.com/13vladimir/foodgram-project-react/actions/workflows/main.yml/badge.svg)

[Ссылка на проект Foodgram](https://pttptt.servehttp.com)

Foodgram - продуктовый помошник в котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. 
Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Технологии
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=blue) ![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E) ![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white) ![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white) ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)

## Установка и запуск проета
### Подготовка проекта

1. Клонировать репозиторий c GitHub и перейти в него в командной строке:
```
git clone https://github.com/<profile_name>/foodgram-project-react.git
cd foodgram-project-react
```

2. Создать в корневой папке файл .env и задать значения атрибутам:
```

Пример секретных ключей расположен в .env.example.

# Параметры Django
    SECRET_KEY=          # секретный ключ Django проекта
    DEBUG=               # отладка проекта
    ALLOWED_HOSTS=       # публичный IP сервера

# Параметры DB PostgreSQL
    POSTGRES_USER=       # postgres user
    POSTGRES_PASSWORD=   # postgres password
    POSTGRES_DB=         # postgres name DB
    DB_HOST=             # postgres host
    DB_PORT=             # postgres port
```

3. Создать секретные атрибуты со значениями в репозитории foodgram-project-react:
```
# Параметры для загрузки образов с DockerHub 
    DOCKER_USERNAME
    DOCKER_PASSWORD

# Параметры для подключения и деплоя проета на удаленном сервере
    HOST
    USER
    SSH_KEY
    SSH_PASSPHRASE

# Параметры телеграмм бота
    TELEGRAM_TO
    TELEGRAM_TOKEN

# Параметры DB PostgreSQL
    POSTGRES_USER
    POSTGRES_PASSWORD
    POSTGRES_DB
    DB_HOST
    DB_PORT
```

### Создание Docker-образов
```
    cd frontend
    docker build -t <username>/foodgram_frontend .
    cd ../backend
    docker build -t <username>/foodgram_backend .
```

### Загрузка образов в репозиторий DockerHub 
```
    docker push <username>/foodgram_frontend
    docker push <username>/foodgram_backend
```

### Подключится к удаленному серверу
```
    ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера 
```

### Создайте на сервере директорию kittygram через терминал
```
    mkdir foodgram
```

### Установите docker compose на сервер

```
    sudo apt update
    sudo apt install curl
    curl -fSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    sudo apt-get install docker-compose-plugin
```

### В директорию foodgram/ скопируйте файл.env
```
    scp -i path_to_SSH/SSH_name .env username@server_ip:/home/username/foodgram/.env
    # ath_to_SSH — путь к файлу с SSH-ключом;
    # SSH_name — имя файла с SSH-ключом (без расширения);
    # username — ваше имя пользователя на сервере;
    # server_ip — IP вашего сервера.
```

### Установка и запуск Nginx на сервере
```
sudo apt install nginx -y
sudo systemctl start nginx
```

### Перейдите в файл конфигурации Nginx и обновите параметры внешнего сервера
```
# Перейти в файл конфигурации Nginx
    sudo nano /etc/nginx/sites-enabled/default

# Параметры внешнего Nginx 
    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8000;
    }
    
# Провоерка файла конфигурации Nginx 
    sudo nginx -t

# Перезапуск Nginx
sudo service nginx reload
```

### Запуск проекта 
 Создайте коммит из корневой папки и отправьте проект с изменениями в репозиторий на GitHub. После успешного деплоя получите сообщениение от телеграмм-бота "Деплой успешно выполнен!".
 ```
 git add .
 git commit -m "<Коммит>"
 git push
 ```
 
 ## Автор
Владимир
@vladim_sa
