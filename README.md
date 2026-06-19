# Foodgram

Foodgram — учебный проект для публикации рецептов.

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

## Как запустить проект на сервере

Клонировать репозиторий:

```bash
git clone https://github.com/ShmykovaAA/foodgram.git
```

Создать файл `.env`:

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

