# 📅 Telegram-бот записи к мастеру

Бот для онлайн-записи клиентов к мастеру (барбер, парикмахер, мастер маникюра,
репетитор и т. п.). Клиент выбирает услугу и свободное время, подтверждает
запись и получает напоминание за час до визита. Мастер управляет расписанием
прямо в чате.

![Демо](docs/demo.gif)

> Демонстрационная GIF-запись кладётся в `docs/demo.gif` — см. `docs/README.md`.

---

## Что умеет

**Клиент**

- 📅 Записаться: услуга → свободный слот → подтверждение.
- 🗒 Мои записи: посмотреть и отменить свои будущие записи.
- ⏰ Автоматическое напоминание за час до визита.
- 🌐 Переключение языка интерфейса: русский / английский.

**Мастер** (определяется по telegram id из `.env`)

- 📆 Расписание на день: занятые, свободные и закрытые слоты.
- ❌ Отменить запись клиента (клиент получает уведомление).
- ➕ Добавить слот вручную (`ГГГГ-ММ-ДД ЧЧ:ММ`).
- ⚪️ Закрыть свободный слот (например, перерыв).

**Под капотом**

- Гонки исключены: слот бронируется атомарно (`INSERT ... WHERE NOT EXISTS`
  + частичный уникальный индекс на подтверждённую запись), поэтому один слот
  не достанется двум клиентам.
- Валидация ввода, обработка ошибок, логирование.
- Rate-limit middleware (защита от флуда).
- Планировщик напоминаний на APScheduler (опрос раз в минуту).

---

## Технологии

- **Python 3.9+** (код и тесты совместимы с 3.9; в Docker используется 3.12).
- **aiogram 3** — Telegram Bot API.
- **APScheduler** — напоминания.
- **PostgreSQL** в проде / **SQLite** локально — выбор через `.env`.
- **aiohttp** — приём вебхуков в проде.

## Структура проекта

```
app/
  config.py        конфигурация из переменных окружения
  states.py        FSM-состояния сценария записи
  texts.py         тексты RU/EN
  keyboards.py     инлайн-клавиатуры (услуги, слоты, подтверждение)
  db.py            слой БД (SQLite / PostgreSQL, единый API)
  dbsetup.py       применение схемы + демо-данные
  repository.py    доступ к данным (весь SQL здесь)
  services.py      чистая бизнес-логика (время слотов, напоминаний)
  scheduler.py     планировщик напоминаний
  middlewares.py   rate-limit + инъекция языка/ролей
  handlers/        обработчики: client.py, master.py
  main.py          точка входа (polling / webhook)
db/                SQL-схемы: 001_init_sqlite.sql, 001_init_postgres.sql
tests/             тесты (занятость слота, FSM, время напоминаний)
```

Модель данных: `masters` → `services` / `slots` → `bookings`.

---

## Быстрый старт (локально, polling)

Нужен Python 3.9+.

```bash
# 1. Клонировать и перейти в папку проекта
cd 08-bot-booking

# 2. Виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Зависимости
pip install -r requirements.txt

# 4. Конфигурация
cp .env.example .env
# откройте .env и впишите BOT_TOKEN и MASTER_IDS (ваш telegram id)

# 5. Запуск
python -m app.main
```

По умолчанию (`MODE=polling`, `DB_DRIVER=sqlite`) бот работает на long polling
и хранит данные в файле `booking.db`. При первом старте автоматически
применяется схема и создаются демо-услуги и несколько слотов на ближайшие дни.

Свой telegram id можно узнать у [@userinfobot](https://t.me/userinfobot).

---

## Запуск в Docker (бот + PostgreSQL)

В комплекте `docker-compose.yml` (бот + Postgres 16). Образ бота — `python:3.12-slim`.

```bash
cp .env.example .env
# заполните BOT_TOKEN, MASTER_IDS, а для вебхука — WEBHOOK_HOST и WEBHOOK_SECRET

docker compose up --build
```

Compose сам выставляет `DB_DRIVER=postgres` и подключает бота к контейнеру БД.
По умолчанию в контейнере включён режим `MODE=webhook` — задайте `WEBHOOK_HOST`
(публичный HTTPS-домен) или переопределите `MODE=polling` для проверки.

---

## Деплой в прод (webhook)

В проде удобнее вебхук вместо polling:

1. Поднимите приложение за HTTPS (обратный прокси с TLS — nginx/Caddy/Traefik —
   перед портом `WEBAPP_PORT`; Telegram принимает только валидный HTTPS).
2. В `.env` задайте:
   - `MODE=webhook`
   - `WEBHOOK_HOST=https://ваш-домен` и `WEBHOOK_PATH=/webhook`
   - `WEBHOOK_SECRET=...` (секрет, который Telegram возвращает для проверки)
   - `DB_DRIVER=postgres` и параметры `DB_*`
3. Запустите (`docker compose up -d` или `python -m app.main`). Бот сам вызовет
   `setWebhook`. Проверка живости — `GET /health` возвращает `ok`.

Переключение polling ↔ webhook и sqlite ↔ postgres — только через `.env`,
код менять не нужно.

---

## Тесты

```bash
pip install -r requirements-dev.txt
pytest
```

Тесты работают на in-memory SQLite и покрывают:

- **занятость слота** — нельзя забронировать занятый/закрытый слот, отмена
  освобождает слот (`tests/test_slots.py`);
- **FSM** — корректный порядок состояний сценария записи (`tests/test_fsm.py`);
- **время напоминания** — расчёт «за час» и выборка «пора напомнить»
  (`tests/test_reminder.py`).

---

## Чек-лист настройки в @BotFather

1. Откройте [@BotFather](https://t.me/BotFather), команда `/newbot`.
2. Задайте имя и username (должен заканчиваться на `bot`).
3. Скопируйте выданный **токен** → в `.env` как `BOT_TOKEN`.
4. `/setdescription` — краткое описание («Запись к мастеру онлайн»).
5. `/setabouttext` — текст в профиле бота.
6. `/setuserpic` — аватарка (по желанию).
7. `/setcommands` — список команд, например:
   ```
   start - Запуск / главное меню
   help - Помощь
   master - Панель мастера
   ```
8. Узнайте свой telegram id через [@userinfobot](https://t.me/userinfobot)
   и впишите в `.env` как `MASTER_IDS` (можно несколько через запятую).
9. Запустите бота и отправьте ему `/start`.

> ⚠️ Токен бота — секрет. Файл `.env` уже добавлен в `.gitignore`, не коммитьте его.
