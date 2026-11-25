# 🔥 Трекер привычек — Telegram Mini App

Полноценное мини-приложение для Telegram: заводишь привычки, отмечаешь выполнение
одним тапом, следишь за сериями (streak) и недельной статистикой. Данные привязаны
к твоему Telegram-аккаунту, а бэкенд проверяет подлинность через подпись `initData`.

> Реальный full-stack: React + Vite фронт, Node + Fastify + PostgreSQL бэк,
> минимальный бот-лаунчер. Не «дизайн по умолчанию» — кастомная тёмная/светлая
> тема под Telegram, тактильная отдача, нативные кнопки.

---

## 📸 Демо

<!-- Вставьте сюда GIF работы приложения (запись экрана из Telegram) -->
<!-- ![Демонстрация](docs/demo.gif) -->

`[ЗДЕСЬ БУДЕТ GIF]` — открытие мини-аппа, создание привычки, отметка, график.

---

## ✨ Возможности

- ➕ Создание и редактирование привычек (эмодзи + цвет-акцент).
- ✅ Отметка выполнения за сегодня одним тапом (toggle).
- 🔥 Текущая и рекордная серия (streak) по каждой привычке.
- 📊 Сводка + недельный столбчатый график выполнения.
- 🗓️ Полоска последних 7 дней в каждой карточке.
- 👤 Данные привязаны к Telegram-аккаунту (у каждого — свои привычки).
- 🎨 Тема, тактильная отдача (haptic), `MainButton` / `BackButton` Telegram.
- 🕳️ Пустые и загрузочные состояния, адаптивная вёрстка.

---

## 🏗️ Архитектура

```
17-miniapp-habits/
├── miniapp/         # Фронтенд: React + Vite + TypeScript + @twa-dev/sdk
│   └── src/
│       ├── lib/         # api-клиент, обёртки Telegram SDK, типы
│       ├── components/  # HabitCard, HabitForm, WeekChart, StatsBar, ...
│       ├── styles/      # тема под Telegram (CSS-переменные)
│       └── App.tsx
├── backend/         # Бэкенд: Node + Fastify + TypeScript
│   ├── db/migrations/   # SQL-схема (users / habits / checkins)
│   └── src/
│       ├── auth/        # ВАЛИДАЦИЯ initData (HMAC) + Fastify-хук авторизации
│       ├── routes/      # REST: /api/habits, /api/stats, /api/me
│       ├── services/    # доступ к БД + расчёт стриков
│       ├── app.ts       # фабрика Fastify (тестируемая через inject)
│       └── server.ts    # точка входа (миграции + listen)
├── bot/             # Минимальный бот-лаунчер (кнопка «Открыть трекер»)
└── docker-compose.yml   # PostgreSQL + backend
```

### Модель данных

| Таблица    | Поля (ключевые)                                              |
|------------|-------------------------------------------------------------|
| `users`    | `id` (Telegram user id, PK), `username`, `first_name`, ...   |
| `habits`   | `id`, `user_id → users`, `title`, `emoji`, `color`, `archived` |
| `checkins` | `id`, `habit_id → habits`, `day` (`YYYY-MM-DD`), UNIQUE(habit_id, day) |

---

## 🔐 Безопасность: валидация Telegram `initData`

Это ключевая часть проекта. Каждый запрос к `/api/*` обязан содержать заголовок
`X-Telegram-Init-Data` со строкой `Telegram.WebApp.initData`. Бэкенд проверяет её
подпись и **только при валидной подписи** пропускает запрос дальше.

Алгоритм (см. `backend/src/auth/initData.ts`, подробные комментарии внутри):

1. Разбираем query-string, извлекаем и убираем поле `hash`.
2. Формируем `data_check_string`: пары `key=value`, отсортированные по ключу,
   склеенные через `\n`.
3. `secret_key = HMAC_SHA256(key="WebAppData", message=BOT_TOKEN)`
   — обратите внимание на **порядок аргументов** (частая ошибка).
4. `computed_hash = HMAC_SHA256(key=secret_key, message=data_check_string)` в hex.
5. Сравниваем с `hash` **constant-time** (`crypto.timingSafeEqual`).
6. Опционально проверяем `auth_date` (защита от replay), лимит — `INITDATA_MAX_AGE_SEC`.

Подделать личность нельзя, не зная `BOT_TOKEN`. Это покрыто тестами: корректная
подпись проходит, любая подмена данных или чужой токен — отклоняются.

---

## 🚀 Локальный запуск

### Вариант A — Docker (Postgres + бэкенд)

```bash
cd 17-miniapp-habits
cp backend/.env.example backend/.env    # укажите BOT_TOKEN
# BOT_TOKEN нужен и как переменная окружения для compose:
export BOT_TOKEN=123456:AA...            # (или задайте в .env для compose)
docker compose up --build
# Бэкенд: http://localhost:8080 (миграции применяются автоматически)
```

### Вариант B — вручную

**Бэкенд:**
```bash
cd backend
cp .env.example .env        # BOT_TOKEN + настройки БД
npm install
# Postgres должен быть запущен (или DB_DRIVER=sqlite для быстрого старта)
npm run migrate             # применить схему
npm run dev                 # http://localhost:8080
```

Для мгновенного старта без Postgres можно временно поставить `DB_DRIVER=sqlite`
в `.env` — тогда данные лягут в локальный файл `habits.sqlite`.

**Фронтенд:**
```bash
cd miniapp
cp .env.example .env        # VITE_API_URL=http://localhost:8080
npm install
npm run dev                 # http://localhost:5173
```

**Бот (по желанию, для кнопки запуска):**
```bash
cd bot
cp .env.example .env        # BOT_TOKEN + MINIAPP_URL (https!)
npm install
npm start
```

> ⚠️ Полноценно приложение работает **внутри Telegram** — там есть `initData`.
> В обычном браузере оно покажет экран «Откройте внутри Telegram» (авторизация
> невозможна без подписи Telegram). Для отладки используйте туннель (ngrok/cloudflared)
> и откройте mini-app через бота.

---

## 🌍 Деплой

### Фронтенд → Vercel (или любая статика)

1. Импортируйте репозиторий в Vercel, **Root Directory** = `miniapp`.
2. Framework preset: **Vite**. Build: `npm run build`, Output: `dist`.
3. Env: `VITE_API_URL=https://<ваш-бэкенд>`.
4. Получите публичный `https://...vercel.app` — это URL mini-app.

### Бэкенд → любой хост с Docker / Node (Railway, Render, VPS)

- Через `docker compose` (Postgres в комплекте) или соберите `backend/Dockerfile`.
- Обязательные env: `BOT_TOKEN`, `DATABASE_URL` (или `DB_*`), `MINIAPP_URL`
  (домен фронта — для CORS), `PORT`.
- Миграции применяются автоматически при старте сервера.

### Подключение WebApp-кнопки в @BotFather

1. Откройте [@BotFather](https://t.me/BotFather) → `/mybots` → ваш бот.
2. **Bot Settings → Menu Button → Configure menu button** → вставьте URL фронта
   (`https://...vercel.app`). Теперь кнопка меню открывает mini-app.
3. (Опционально) `/newapp` — создать именованное mini-app с картинкой и short-name.
4. Убедитесь, что домен фронта — **HTTPS** (требование Telegram для `web_app`).

---

## 🧪 Тесты

```bash
cd backend
npm test
```

Покрыто:
- **initData**: корректная подпись проходит; подделанные данные и чужой токен
  отклоняются; просроченный `auth_date` отклоняется.
- **Стрики**: текущая/рекордная серия, разрывы, дубли, недельная выборка.
- **API (интеграция на SQLite in-memory)**: запрос без/с подделанным `initData` → 401;
  создание, toggle, статистика, удаление.

---

## ✅ Чек-лист перед публикацией

- [ ] `BOT_TOKEN` задан в `backend/.env` (и не попал в git — он в `.gitignore`).
- [ ] Postgres доступен, `npm run migrate` отработал (или Docker поднял БД).
- [ ] Фронт задеплоен по HTTPS, `VITE_API_URL` указывает на прод-бэкенд.
- [ ] `MINIAPP_URL` на бэке = домен фронта (иначе CORS заблокирует запросы).
- [ ] В @BotFather настроена Menu Button / WebApp с URL фронта.
- [ ] Открыли mini-app через бота, создали привычку, отметили — данные сохранились.
- [ ] `npm test` (backend) — зелёный.
- [ ] Записан GIF и вставлен в раздел «Демо».

---

## 🛠️ Стек

React 18 · Vite · TypeScript · @twa-dev/sdk · Node.js · Fastify · PostgreSQL (`pg`)
· better-sqlite3 (локально/тесты) · Vitest · Docker.
