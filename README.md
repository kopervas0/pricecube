# PriceCube — аналитика маркетплейса (микросервисы)

> Fullstack-проект-витрина: **Django + React**, микросервисы в Docker, фоновая синхронизация
> через **Celery + Redis**, **PostgreSQL**, фронтенд на **Vite + TypeScript**.

Решает задачу автоматизации ценообразования и аналитики для магазинов на **Ozon / Wildberries**:
агрегирует товары, цены и остатки, отдаёт их в дашборд и фоном синхронизирует с Seller API.

---

## Возможности

- 📦 **Каталог товаров** — поиск, фильтр по категориям, пагинация.
- 📊 **Дашборд-аналитика** — количество, средняя цена, остатки, распределение по категориям (гистограмма).
- 💹 **История цен** — каждое изменение пишется в `PriceHistory`, готово под график.
- ⚙️ **Фоновая синхронизация** — Celery + beat каждые 15 мин тянет данные из Ozon Seller API.
- 🧪 **Демо-режим** — если в магазине нет товаров, генерируются реалистичные тестовые данные (`DEMO_MODE=true`).
- 🐳 **Всё в Docker** — один `docker compose up` поднимает 5 сервисов.

## Стек (соответствие вакансии Fullstack Django + React)

| Область | Технологии |
|---|---|
| Backend | Python, Django 5, Django REST Framework |
| Фоновые задачи | Celery, Redis (broker + beat) |
| База данных | PostgreSQL 16, SQL, ORM |
| Frontend | JavaScript, TypeScript, React 19, Vite |
| Инфраструктура | Docker, Docker Compose, GitHub Actions |
| Интеграции | Ozon Seller API, HTTP, JSON, пагинация |
| Подход | data-driven аналитика, MVVM-слои, чистая архитектура |

---

## Архитектура

```
┌──────────────────┐      ┌───────────────────┐      ┌────────────┐
│  frontend        │ ───▶ │  api (Django)     │ ───▶ │ PostgreSQL │
│  React + Vite    │      │  REST / proxy     │      └────────────┘
│  :5173           │      │  :8000            │            ▲
└──────────────────┘      └─────────┬─────────┘            │
                                    │                      │
                          ┌─────────▼─────────┐    ┌───────┴──────┐
                          │  worker (Celery)  │ ─▶ │    Redis     │
                          │  sync / beat      │    │   broker     │
                          └─────────┬─────────┘    └──────────────┘
                                    │
                     ┌──────────────┴───────────────┐
                     ▼                              ▼
           Ozon Seller API                 demo-seed (нет товаров)
```

| Сервис | Образ | Порт | Назначение |
|---|---|---|---|
| `frontend` | `pricecube-frontend` | 5173 | UI дашборда, проксирует `/api` |
| `api` | `pricecube-api` | 8000 | Django REST, единственный ходит в Ozon |
| `worker` | `pricecube-worker` | — | Celery: синхронизация, beat-расписание |
| `db` | `postgres:16-alpine` | 5432 | PostgreSQL |
| `redis` | `redis:7-alpine` | 6379 | Брокер задач |

---

## Быстрый старт

```bash
git clone https://github.com/kopervas0/pricecube.git
cd pricecube

# 1. Переменные окружения (demo-режим включён по умолчанию)
copy .env.example .env          # Windows
# cp .env.example .env          # macOS/Linux

# 2. Поднять всё
docker compose up --build

# 3. Наполнить демо-данными (или дождаться beat-синхронизации)
#    откройте в браузере кнопку «Синхронизировать» либо:
curl -X POST http://localhost:8000/api/products/sync/
```

- 🖥 Дашборд: **http://localhost:5173**
- 🔌 API: **http://localhost:8000/api/products/**
- 💚 Health: **http://localhost:8000/api/health/**

---

## Режимы данных

Проект решает проблему «в магазине пока нет товаров» переключаемым режимом в `.env`:

| Режим | Флаг | Поведение |
|---|---|---|
| Демо | `DEMO_MODE=true` | Генерируются тестовые товары, фронт работает от реального API. Ничего добавлять руками не нужно. |
| Прод | `DEMO_MODE=false` | Реальный **Ozon Seller API** по вашему ключу. Как только в кабинете появится товар — `sync_products` его подхватит. |

Ключи в `.env` (файл в `.gitignore`, в репозиторий не попадает):

```env
OZON_API_KEY=...
OZON_CLIENT_ID=...
OZON_API_HOST=https://api-seller.ozon.ru
```

---

## API

| Метод | Путь | Описание |
|---|---|---|
| GET | `/api/health/` | статус и текущий режим |
| GET | `/api/products/` | список товаров (`?search=&category=&page=`) |
| GET | `/api/products/stats/` | агрегаты для дашборда |
| GET | `/api/products/{id}/history/` | история цен (для графика) |
| POST | `/api/products/sync/` | ручной запуск синхронизации |

---

## Структура репозитория

```
pricecube/
├── docker-compose.yml        # оркестрация 5 сервисов
├── .env.example              # шаблон переменных
├── backend/                  # Django + DRF + Celery
│   ├── manage.py
│   ├── requirements.txt
│   ├── pricecube/            # настройки, urls, celery
│   └── core/                 # models, views, tasks, ozon-клиент
└── frontend/                 # React + Vite + TS
    ├── vite.config.ts        # прокси /api → api:8000
    └── src/                  # App, api-client, типы, стили
```

---

## Roadmap

- [x] Микросервисная архитектура, Docker Compose
- [x] Django REST API + PostgreSQL + миграции
- [x] Celery + Redis фоновая синхронизация
- [x] React-дашборд с поиском и аналитикой
- [x] Демо-режим для запуска без товаров
- [ ] График истории цен (Chart.js, данные уже есть)
- [ ] Экспорт отчётов (pandas → CSV/XLSX)
- [ ] Интеграция с Wildberries API
- [ ] Деплой (GitHub Actions → Pages / сервер)

---

## Лицензия

MIT · Сделано как портфолио-проект для позиции Fullstack-разработчик.
