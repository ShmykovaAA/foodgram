# Foodgram

Foodgram — учебный проект для публикации рецептов.
Ссылка на страницу проекта: http://kittygrammmyapr.servecounterstrike.com

В проекте можно:

* регистрироваться и входить в аккаунт;
* создавать, редактировать и удалять рецепты;
* добавлять рецепты в избранное;
* добавлять рецепты в список покупок;
* подписываться на авторов;
* скачивать список покупок;
* загружать изображение рецепта и аватар пользователя.

## Стек

Backend:

* Python
* Django
* Django REST Framework
* Djoser
* PostgreSQL

Инфраструктура:

* Docker
* Docker Compose
* Nginx
* Gunicorn


## Как запустить проект

### Локальный запуск проекта

Клонируйте репозиторий:

```bash
git clone https://github.com/ShmykovaAA/foodgram.git
cd foodgram/backend
```

Создайте и активируйте виртуальное окружение.

Для Windows:

```bash
python -m venv venv
source venv/Scripts/activate
```

Для Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Установите зависимости:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Создайте файл `.env` в директории `backend/` и заполните переменные окружения:

```env
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=localhost
DB_PORT=5432
```

Выполните миграции:

```bash
python manage.py migrate
```

Создайте суперпользователя:

```bash
python manage.py createsuperuser
```

Запустите сервер разработки:

```bash
python manage.py runserver
```

Проект будет доступен по адресу:

```text
http://127.0.0.1:8000/
```

Админ-зона доступна по адресу:

```text
http://127.0.0.1:8000/admin/
```

---

### Запуск проекта на сервере с помощью Docker

Подключитесь к серверу:

```bash
ssh username@server_ip
```

Клонируйте репозиторий:

```bash
git clone https://github.com/ShmykovaAA/foodgram.git
cd foodgram/infra
```

Создайте файл `.env` в директории `infra/`:

```bash
nano .env
```

Пример содержимого `.env`:

```env
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432

SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=your_domain,localhost,127.0.0.1
```

Запустите контейнеры:

```bash
docker compose -f docker-compose.production.yml up -d --build
```

Выполните миграции:

```bash
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

Соберите статические файлы:

```bash
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput
```

Скопируйте статические файлы в volume, если это предусмотрено конфигурацией проекта:

```bash
docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

Создайте суперпользователя:

```bash
docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

Проверьте статус контейнеров:

```bash
docker compose -f docker-compose.production.yml ps
```

Проект будет доступен по адресу:

```text
http://your_domain/
```

Админ-зона доступна по адресу:

```text
http://your_domain/admin/
```
---

## Основные адреса

Админка:

```text
/admin/
```

API:

```text
/api/
```

Рецепты:

```text
/api/recipes/
```

Пользователи:

```text
/api/users/
```

Теги:

```text
/api/tags/
```

Ингредиенты:

```text
/api/ingredients/
```

## Автор Шмыкова Анна

Учебный проект выполнен в рамках курса по backend-разработке.

