# Анонимная обратная связь сотрудников

Внутреннее веб-приложение: сотрудники без авторизации оставляют анонимные отзывы и
идеи, администратор входит по логину/паролю и модерирует их.

Подробное описание устройства каждого сервиса — в [`DOCUMENTATION.md`](./DOCUMENTATION.md).

## Запуск одной командой

```bash
docker compose up --build
```

Открыть в браузере: **http://localhost/**

Ступенчатый старт (через healthcheck'и и `depends_on`):

1. `postgres` — стартует и ждёт готовности (`pg_isready`);
2. `backend` и `frontend` — стартуют только когда БД healthy;
3. `proxy` — стартует только когда backend и frontend healthy.

## Быстрый запуск без Docker (локально)

Если Docker недоступен, приложение можно запустить **одним процессом** на SQLite —
FastAPI отдаёт и API, и собранный SPA:

```bash
./run-local.sh
```

Затем открыть **http://localhost:8080/** (админ `admin` / `password`). Это тот же код;
отличается только слой данных: на SQLite `id`/время генерируются на стороне приложения
(на PostgreSQL — на стороне БД через `uuidv7()`/`now()`), а схема создаётся
автоматически при старте (в production ею по-прежнему управляет Alembic).

## Порты на хосте

| Порт | Сервис   | Назначение                                       |
|------|----------|--------------------------------------------------|
| 80   | nginx    | Точка входа для браузера (HTTP, без шифрования)   |
| 8080 | backend  | Прямой доступ к API для тестирования             |
| 5432 | postgres | Ручная работа с БД и регистрация админов         |

## Учётные данные по умолчанию

- Приложение (админ): `admin` / `password` — создаётся первой миграцией.
- PostgreSQL: роль `admin` / `password`, база `feedback`.

## Структура

```
anon-feedback/
├── docker-compose.yml
├── DOCUMENTATION.md          # подробная документация по каждому сервису
├── nginx/default.conf        # обратный прокси
├── backend/
│   ├── src/feedback_app/     # исходники по слоям
│   │   ├── core/  models/  schemas/  repositories/  services/  controllers/
│   │   └── main.py
│   ├── tests/                # pytest: unit + integration
│   └── alembic/              # миграции БД
└── frontend/
    ├── src/                  # api/ lib/ hooks/ components/ pages/ styles/
    └── tests/                # vitest + testing-library
```

Слои бэкенда (однонаправленная зависимость): `controllers → services →
repositories → БД`; `models` (Model), `schemas` (View), `controllers` (Controller) —
явные слои MVC. Обработка ошибок — исключениями на всех уровнях, кроме уровня данных
(репозитории возвращают значения/`None`).

## REST API

| Метод  | Путь                     | Доступ | Описание                                        |
|--------|--------------------------|--------|-------------------------------------------------|
| POST   | `/api/feedbacks`         | все    | Создать отзыв `{topic, body}` (оба обязательны) |
| POST   | `/api/auth/login`        | все    | `{login, password}` → `{access_token}` или 401  |
| GET    | `/api/feedbacks`         | админ  | `?page=&order=asc\|desc&date_from=&date_to=` (по 50) |
| DELETE | `/api/feedbacks/{id}`    | админ  | Удалить отзыв                                   |
| GET    | `/api/health`            | все    | Проверка живости                                |

## Тесты

```bash
# backend
cd backend && pip install -r requirements-dev.txt && pytest

# frontend
cd frontend && npm install && npm test
```

## Регистрация новых администраторов

Через открытый порт 5432 (`id` заполнит БД):

```bash
psql postgresql://admin:password@localhost:5432/feedback \
  -c "INSERT INTO users (login, password) VALUES ('hr_lead', 'секрет');"
```

## Безопасность

Пароли администраторов хранятся в открытом виде, а трафик идёт по HTTP без
шифрования — намеренно, по условию задачи (полностью внутренний сервис, регистрация
вручную через БД). Допустимо только внутри доверенной сети; перед расширением
периметра добавьте хеширование паролей и TLS.
