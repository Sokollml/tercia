# ☕ Карта лояльности — Telegram Mini App

Мини-приложение для кофейни: гость собирает штампы за каждый напиток, после
**N** штампов получает награду, а карта обнуляется. Бариста начисляет штампы
сканированием QR-кода гостя или вводом кода вручную и видит статистику кафе.

Полноценный проект с реальным бэкендом: проверка подписи Telegram `initData`,
роли клиент/админ, защита от повторного скана, PostgreSQL.

---

## 🎬 Демо

> _Место для GIF-демонстрации._
>
> ![Демо мини-приложения](docs/demo.gif)
>
> _Слева — карта гостя с QR, справа — панель бариста с начислением штампа и наградой._

---

## 🧭 Путь «штамп → награда»

```
Гость открывает мини-апп
        │
        ▼
Бэкенд проверяет initData (HMAC) → создаёт карту (код LOY-XXXX-XXXX)
        │
        ▼
Гость показывает QR / код бариста
        │
        ▼
Бариста в своей панели: «Сканировать QR» или ввод кода
        │
        ▼
POST /api/admin/stamp { code, idempotencyKey }
        │
        ├─ не админ?  → 403 (отклонено до записи в БД)
        ├─ дубль скана (тот же idempotencyKey)? → штамп не начисляется повторно
        │
        ▼
applyStamp():  stamps + 1
        │
        ├─ stamps < N  → «до награды: N − stamps», карта обновлена
        └─ stamps = N  → 🎁 награда! rewardsEarned + 1, stamps → 0 (сброс)
```

Порог `N` задаётся переменной `STAMPS_PER_REWARD` (по умолчанию 8).

---

## 🏗 Архитектура

| Часть        | Стек                                   | Папка       |
| ------------ | -------------------------------------- | ----------- |
| Фронтенд     | React + Vite + TypeScript + `@twa-dev/sdk` | `miniapp/`  |
| Бэкенд       | Node + Fastify + TypeScript, `pg`      | `backend/`  |
| База данных  | PostgreSQL (`users`, `cards`, `stamps`) | `backend/db/schema.sql` |
| Бот-лаунчер  | Node + grammy                          | `bot/`      |
| Инфраструктура | Docker Compose (db + backend + bot)  | `docker-compose.yml` |

### Модель данных

- **users** — все, кто открыл приложение; флаг `is_admin` задаётся сервером по
  `ADMIN_IDS`, а не приходит от клиента.
- **cards** — одна карта на пользователя: текущие штампы, всего наград, уникальный
  код для QR.
- **stamps** — неизменяемый журнал всех начислений: аудит, статистика и
  идемпотентность (уникальный `idempotency_key` → защита от двойного скана).

### Безопасность

- **Проверка `initData`** (`backend/src/lib/telegram.ts`): каждый запрос к `/api`
  несёт подписанный Telegram `initData` в заголовке `x-telegram-init-data`.
  Секретный ключ выводится как `HMAC_SHA256(key="WebAppData", message=bot_token)`,
  затем сверяется HMAC строки данных (constant-time сравнение) + проверка свежести
  `auth_date`. Без валидной подписи — `401`.
- **Роли**: пользователь считается админом, только если его Telegram id есть в
  `ADMIN_IDS` (серверная переменная окружения).
- **Начисление штампа** доступно **только админу**; неадмин отклоняется до любой
  записи в БД. Повтор `idempotency_key` не начисляет второй штамп.

---

## 🚀 Быстрый старт (локально, Docker)

Нужен бот в [@BotFather](https://t.me/BotFather) и его токен, а также ваш
Telegram id (узнать — [@userinfobot](https://t.me/userinfobot)).

```bash
cp .env.example .env
# заполните BOT_TOKEN, ADMIN_IDS, MINIAPP_URL

docker compose up -d --build
docker compose exec backend npm run migrate   # создать таблицы
```

Бэкенд поднимется на `http://localhost:3000`, бот запустится в режиме long
polling. Фронтенд деплоится отдельно (Telegram требует HTTPS — см. ниже).

### Запуск без Docker

```bash
# 1. PostgreSQL (например, локально) + примените схему:
cd backend && cp .env.example .env   # заполните значения
npm install && npm run migrate
npm run dev            # API на http://localhost:3000

# 2. Фронтенд
cd ../miniapp && cp .env.example .env  # VITE_API_URL=http://localhost:3000
npm install && npm run dev             # http://localhost:5173

# 3. Бот
cd ../bot && cp .env.example .env
npm install && npm run dev
```

---

## 🌐 Деплой

1. **Фронтенд** → Vercel / Netlify / Cloudflare Pages.
   - Root: `miniapp/`, build: `npm run build`, output: `dist/`.
   - Переменная `VITE_API_URL` = публичный URL бэкенда.
   - Получите публичный HTTPS-URL — это `MINIAPP_URL`.
2. **Бэкенд + БД** → любой хост с Docker (Railway, Fly.io, VPS) или managed
   Postgres + `docker compose up backend`. Задайте все переменные из `.env.example`.
3. **Mini App в BotFather**: `/newapp` (или `/setmenubutton`) → укажите
   `MINIAPP_URL`. Бот сам ставит кнопку меню при старте.
4. Примените миграции: `npm run migrate` (или `docker compose exec backend npm run migrate`).

---

## 🧪 Тесты и проверки

```bash
# Бэкенд: типы, сборка, тесты
cd backend && npm install && npm run typecheck && npm run build && npm test

# Фронтенд: типы + сборка
cd ../miniapp && npm install && npm run build
```

Тесты покрывают ключевую логику (`backend/test/`):

- `loyalty.test.ts` — N-й штамп даёт награду и **сбрасывает** карту, несколько циклов.
- `service.test.ts` — неадмин **отклонён**; идемпотентность (двойной скан = один штамп); неизвестный код.
- `telegram.test.ts` — валидный `initData` принимается; чужой токен / подмена данных / просроченный `auth_date` — отклоняются.

---

## ✅ Чек-лист перед запуском в прод

- [ ] `BOT_TOKEN` задан и **не** в репозитории (`.env` в `.gitignore`).
- [ ] `ADMIN_IDS` содержит id всех сотрудников кафе.
- [ ] `MINIAPP_URL` = реальный HTTPS-адрес фронтенда, он же прописан в BotFather.
- [ ] `VITE_API_URL` на фронте указывает на публичный бэкенд, CORS настроен.
- [ ] Применены миграции (`npm run migrate`), таблицы созданы.
- [ ] PostgreSQL с включённым SSL в проде (`DB_SSL=true` или `DATABASE_URL`).
- [ ] `STAMPS_PER_REWARD` установлен под вашу акцию.
- [ ] Проверено: гость видит карту и QR; бариста начисляет штамп; на N-м —
      награда и сброс; повторный скан не даёт второй штамп; неадмин не может
      начислить штамп.
- [ ] `npm test` (бэкенд) и `npm run build` (фронт) проходят.

---

## 📁 Структура

```
18-miniapp-loyalty/
├── backend/            # Fastify API
│   ├── db/schema.sql   # таблицы users / cards / stamps
│   ├── src/
│   │   ├── lib/        # telegram (initData), loyalty (правила), code (генерация)
│   │   ├── app.ts      # роуты + обработка ошибок
│   │   ├── auth.ts     # preHandler: проверка initData, роль, upsert
│   │   ├── service.ts  # бизнес-операции + авторизация
│   │   ├── pg-store.ts # реализация хранилища на PostgreSQL
│   │   └── index.ts    # точка входа
│   └── test/           # vitest
├── miniapp/            # React + Vite mini-app
│   └── src/
│       ├── components/ # StampCard, ClientView, AdminView, QrCode
│       └── lib/        # api, telegram (SDK), types
├── bot/                # grammy bot-лаунчер
├── docker-compose.yml
└── .env.example
```
