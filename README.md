# PriceCube — аналитика маркетплейса (микросервисы)

Fullstack-проект под вакансию **Django + React**: микросервисы в Docker,
фоновая синхронизация через Celery + Redis, PostgreSQL, фронтенд на Vite + TypeScript.

## Архитектура

```
frontend (React+Vite)  →  api (Django REST)  →  PostgreSQL
                                  ↓
                            worker (Celery)  →  Redis
                                  ↓
                         Ozon Seller API  |  demo-seed (нет товаров)
```

| Сервис | Стек | Порт |
|---|---|---|
| frontend | React 19, Vite, TypeScript | 5173 |
| api | Django 5, DRF | 8000 |
| worker | Celery | — |
| db | PostgreSQL 16 | 5432 |
| redis | Redis 7 | 6379 |

## Режимы данных

Проект решает проблему «в магазине нет товаров» через **переключаемый режим**:

- `DEMO_MODE=true` — генерируются демо-товары (seed), фронтенд работает от реального API,
  но данные тестовые. Ничего руками добавлять не нужно.
- `DEMO_MODE=false` — реальный **Ozon Seller API** по вашему ключу.
  Как только в кабинете появится товар, `sync_products` его подхватит.

Переключается в `.env`.

## Запуск

```bash
cd D:\vaib\pricecube
copy .env.example .env      # Windows: заполните OZON_* при необходимости
docker compose up --build
```

- Дашборд: http://localhost:5173
- API: http://localhost:8000/api/products/
- Health: http://localhost:8000/api/health/

## API

| Метод | Путь | Описание |
|---|---|---|
| GET | `/api/products/` | список товаров (`?search=&category=`) |
| GET | `/api/products/stats/` | агрегаты для дашборда |
| GET | `/api/products/{id}/history/` | история цен |
| POST | `/api/products/sync/` | ручной запуск синхронизации |

## Что показывает дашборд

- карточки: товары, средняя цена, остаток, категории;
- таблица с поиском и фильтром по категории;
- гистограмма распределения по категориям;
- бейдж режима (demo / Ozon API).

## Стек (соответствие вакансии)

Python · Django · DRF · Celery · Redis · PostgreSQL · SQL ·
JavaScript · TypeScript · React · Vite · Docker · data-driven аналитика.
