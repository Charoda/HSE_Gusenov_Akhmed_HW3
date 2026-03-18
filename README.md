# URL Shortener API

Сервис на FastAPI для сокращения URL с аналитикой, кэшированием и функциями управления.

## Возможности

### Обязательные функции (5)
1. **Создание/Удаление/Обновление/Получение коротких ссылок**
   - `POST /links/shorten` - Создать короткую ссылку
   - `GET /links/{short_code}` - Перенаправление на оригинальный URL
   - `DELETE /links/{short_code}` - Удалить ссылку
   - `PUT /links/{short_code}` - Обновить URL ссылки

2. **Статистика по ссылке**
   - `GET /links/{short_code}/stats` - Просмотр аналитики ссылки

3. **Пользовательские алиасы**
   - Поддержка пользовательских коротких кодов через параметр `custom_alias`

4. **Поиск по оригинальному URL**
   - `GET /links/search?original_url={url}` - Найти все ссылки для URL

5. **Срок действия ссылки**
   - Параметр `expires_at` для автоматического удаления

### Дополнительные функции (2+)
- **Очистка истекших ссылок** - `POST /links/cleanup/expired`
- **Очистка неиспользуемых ссылок** - `POST /links/cleanup/unused?days=90`
- **Кэширование Redis** - Все запросы ссылок кэшируются
- **Аутентификация** - Регистрация пользователей и JWT токены
- **Контроль доступа** - Обновление/Удаление только для владельцев ссылок

## Технологический стек

- **FastAPI** - Веб-фреймворк
- **PostgreSQL** - Основная база данных
- **Redis** - Слой кэширования
- **SQLAlchemy** - ORM
- **JWT** - Аутентификация
- **Docker** - Контейнеризация

## Быстрый старт

### Требования
- Docker & Docker Compose
- Python 3.11+ (для локальной разработки)

### Использование Docker Compose (Рекомендуется)

1. Клонирование и настройка:
```bash
cp .env.example .env
# Отредактируйте .env с вашими настройками
```

2. Запуск всех сервисов:
```bash
docker-compose up -d
```

3. API будет доступен по адресу: `http://localhost:8000`
   - Интерактивная документация: `http://localhost:8000/docs`
   - Проверка здоровья: `http://localhost:8000/health`

### Локальная разработка

1. Установка зависимостей:
```bash
pip install -r requirements.txt
```

2. Настройка окружения:
```bash
cp .env.example .env
# Настройте DATABASE_URL и REDIS_URL в .env
```

3. Запуск приложения:
```bash
uvicorn app.main:app --reload
```

## Документация API

### Аутентификация

#### Регистрация нового пользователя
```http
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

#### Вход
```http
POST /auth/login?username=john_doe&password=securepassword123
```

Возвращает: `{"access_token": "...", "token_type": "bearer"}`

Используйте токен в последующих запросах:
```http
Authorization: Bearer <your_token>
```

### Ссылки

#### Создание короткой ссылки
```http
POST /links/shorten
Content-Type: application/json

{
  "original_url": "https://very-long-url.com/with/many/segments",
  "custom_alias": "mylink",
  "expires_at": "2024-12-31T23:59:00"
}
```

Ответ:
```json
{
  "id": 1,
  "short_code": "mylink",
  "original_url": "https://very-long-url.com/with/many/segments",
  "custom_alias": "mylink",
  "clicks": 0,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

#### Перенаправление (использование короткой ссылки)
```http
GET /links/{short_code}
```
Возвращает 307 перенаправление на оригинальный URL.

#### Получение статистики ссылки
```http
GET /links/{short_code}/stats
```

Ответ:
```json
{
  "original_url": "https://very-long-url.com/with/many/segments",
  "short_code": "mylink",
  "created_at": "2024-01-01T00:00:00",
  "clicks": 42,
  "last_clicked_at": "2024-01-15T10:30:00",
  "is_active": true,
  "expires_at": null
}
```

#### Обновление ссылки
```http
PUT /links/{short_code}
Content-Type: application/json

{
  "original_url": "https://new-url.com"
}
```

#### Удаление ссылки
```http
DELETE /links/{short_code}
```

#### Поиск по оригинальному URL
```http
GET /links/search?original_url=https://very-long-url.com/with/many/segments
```

#### Очистка истекших ссылок (только для админов/владельцев)
```http
POST /links/cleanup/expired
```

#### Очистка неиспользуемых ссылок (только для админов/владельцев)
```http
POST /links/cleanup/unused?days=90
```

## Схема базы данных

### Пользователи
- `id` - Первичный ключ
- `username` - Уникальный
- `email` - Уникальный
- `hashed_password` - BCrypt хэш
- `is_active` - Флаг активности
- `created_at` - Метка времени

### Ссылки
- `id` - Первичный ключ
- `short_code` - Уникальный короткий идентификатор
- `original_url` - Полный URL
- `custom_alias` - Опциональный пользовательский короткий код
- `user_id` - Внешний ключ на пользователей (может быть NULL для анонимных)
- `clicks` - Счетчик кликов
- `last_clicked_at` - Метка времени последнего клика
- `expires_at` - Опциональная метка времени истечения
- `is_active` - Флаг активности
- `created_at` - Метка времени

## Стратегия кэширования

- **Redis** используется для кэширования запросов ссылок
- Формат ключа кэша: `link:{short_code}`
- TTL: 1 час (3600 секунд)
- Кэш инвалидируется при:
  - Создание ссылки
  - Обновление ссылки
  - Удаление ссылки
  - Клик по ссылке (обновление статистики)

## Контроль доступа

- **GET** эндпоинты публичные (аутентификация не требуется)
- **POST/PUT/DELETE** эндпоинты требуют аутентификацию для:
  - Ссылок, созданных аутентифицированными пользователями
  - Анонимные ссылки могут управляться кем угодно (без user_id)
- Для ограничения управления только владельцами, убедитесь что вы аутентифицированы

## Переменные окружения

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=url_shortener
```

## Структура проекта

```
.
├── app/
│   ├── api/
│   │   ├── auth_router.py    # Эндпоинты аутентификации
│   │   └── links_router.py   # Эндпоинты управления ссылками
│   ├── services/
│   │   └── link_service.py   # Бизнес-логика для ссылок
│   ├── utils/
│   │   ├── security.py       # Утилиты для паролей и JWT
│   │   └── redis_client.py   # Redis клиент для кэширования
│   ├── __init__.py
│   ├── main.py               # Приложение FastAPI
│   ├── config.py             # Конфигурация
│   ├── database.py           # Подключение к базе данных
│   ├── models.py             # Модели SQLAlchemy
│   ├── schemas.py            # Схемы Pydantic
│   └── initialization.py     # Инициализация при запуске
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## Тестирование API

1. Запускал сервер в Render.com
3. Зарегистрируйте пользователя через `/auth/register`
4. Создайте короткую ссылку через `/links/shorten`
5. Перейдите по короткой ссылке через браузер или `GET /links/{short_code}`
6. Просмотрите статистику через `/links/{short_code}/stats`


MIT