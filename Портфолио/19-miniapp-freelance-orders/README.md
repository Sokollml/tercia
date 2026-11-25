# Freelance Orders — Telegram mini-app поиска фриланс-заказов

Мини-приложение для Telegram, которое собирает сообщения-заказы из **публичных**
чатов, где ищут исполнителей, прогоняет их через ИИ-классификацию и показывает
пользователю удобную ленту: с фильтрами, статусами и личными заметками.
Отклик на заказ пользователь пишет **сам** — приложение только помогает найти
подходящие заказы и открыть исходное сообщение в Telegram.

> Портфолио-проект. Ниже — архитектура, риски, пошаговая сборка и верификация.

<!-- ============================================================
     МЕСТО ДЛЯ ДЕМО-GIF
     Запиши экран мини-аппа (лента → карточка → «Открыть в Telegram» → настройки)
     и вставь сюда:
     ![Демо мини-аппа](docs/demo.gif)
     ============================================================ -->
`[ЗДЕСЬ БУДЕТ GIF: лента заказов → карточка → «Открыть в Telegram» → настройки]`

---

## Архитектура

```mermaid
flowchart TD
    subgraph TG["Telegram (публичные чаты)"]
        C1["@freelance_chat"]
        C2["@design_orders"]
    end

    subgraph COL["collector/ — Python + Telethon (userbot, ТОЛЬКО чтение)"]
        R["read новых/исторических сообщений"]
        PF["префильтр: ключевые/стоп-слова"]
        DD["дедуп: sha256 нормализованного текста"]
    end

    subgraph DB[("PostgreSQL")]
        RAW["raw_messages (pending)"]
        ORD["orders"]
        USR["users / user_order_status"]
    end

    subgraph N8N["n8n workflows"]
        CLS["classify.json:<br/>Schedule → SELECT pending →<br/>AI Agent (строгий JSON) →<br/>Code parse+fallback →<br/>INSERT orders → mark done"]
        API["api.json:<br/>Webhook-эндпоинты +<br/>валидация initData (HMAC)"]
    end

    subgraph APP["miniapp/ — React + Vite + TS"]
        FEED["Лента заказов"]
        CARD["Карточка заказа<br/>(Открыть в Telegram, статус, заметка)"]
        SET["Мои настройки"]
    end

    C1 & C2 --> R --> PF --> DD --> RAW
    RAW --> CLS --> ORD
    API <--> ORD
    API <--> USR
    APP <-->|"HTTPS + X-Telegram-Init-Data"| API
    U["Пользователь"] -->|"пишет отклик сам"| TG
```

Поток данных: **чаты → collector → `raw_messages` → n8n classify → `orders` →
n8n api → mini-app**. Настройки и статусы пользователя живут в `users` и
`user_order_status`.

---

## ⚠️ БАН-РИСКИ И ПРАВИЛА БЕЗОПАСНОСТИ (ЧИТАТЬ ПЕРВЫМ)

Collector — это **userbot** на Telethon, работающий от имени реального аккаунта.
Telegram не любит автоматизацию и **может заблокировать аккаунт**. Чтобы снизить
риск, проект намеренно устроен консервативно:

### 🔴 ТОЛЬКО ЧТЕНИЕ
Collector **никогда** не пишет сообщения, не ставит реакции, не вступает в чаты
и не подписывается автоматически. Он лишь читает историю/новые сообщения из
чатов, куда ты **уже вступил вручную обычным способом**. Только **публичные**
чаты/каналы. Никакого парсинга закрытых групп.

### 🔴 ОТДЕЛЬНЫЙ АККАУНТ
Используй **отдельный** номер/аккаунт, а **не основной**. Если аккаунт улетит в
бан — ты не потеряешь личную переписку и контакты.

### 🔴 ТРОТТЛИНГ
Между чатами и между сообщениями стоят паузы (`throttle` в `config.yaml`,
по умолчанию 5 c и 0.5 c). **Не ставь 0.** Чем «человечнее» ритм — тем ниже
риск. Историю тяни разумными порциями (`history_limit`), не миллионами.

### 🔴 СЕССИЯ — В VOLUME, НЕ В РЕПОЗИТОРИИ
Файл сессии Telethon (`*.session`) = доступ к аккаунту. Он лежит в volume
(`TG_SESSION=/data/session/collector.session`) и занесён в `.gitignore`.
**Никогда не коммить `*.session` и `.env`.**

> Эти меры снижают риск, но не отменяют его. Автоматизация userbot-ом всегда
> противоречит духу ToS Telegram — держи это в голове и не используй важный аккаунт.

---

## Состав репозитория

| Часть | Путь | Что делает |
|---|---|---|
| Сборщик | `collector/` | Telethon userbot: чтение публичных чатов → префильтр → дедуп → `raw_messages`. `export_history.py` — разовая выгрузка истории. |
| Классификация | `workflows/classify.json` | n8n: Schedule → SELECT необработанных → AI Agent (строгий JSON) → Code (парсинг + fallback) → INSERT `orders` → пометка обработанных. |
| API | `workflows/api.json` | n8n: webhook-эндпоинты (лента с фильтрами+пагинацией, get/update настроек, статус заказа) + валидация `initData` (HMAC) в Code-ноде. |
| Мини-апп | `miniapp/` | React + Vite + TS + `@twa-dev/sdk`: лента, настройки, карточка заказа. |
| Схема БД | `db/001_orders.sql` | `raw_messages`, `orders`, `users`, `user_order_status`. |
| Промпт | `prompts/order_classifier.txt` | Системный промпт ИИ-классификатора. |
| Валидатор | `validator/` | Эталонная Python-реализация проверки `initData` + опциональный HTTP-микросервис (та же логика продублирована в Code-ноде `api.json`). |

---

## Пошаговая сборка

### 0. Секреты
```bash
cp .env.example .env
# заполни .env: TG_API_ID/HASH/PHONE, BOT_TOKEN, DB_*, LLM_*
```

### 1. База данных
```bash
psql "$DATABASE_URL" -f db/001_orders.sql   # идемпотентно, можно повторять
```

### 2. Collector (Telethon userbot)
> venv лучше держать **не на внешнем диске** (внешний ломает Python об `._*.pth`),
> а на внутреннем — например в `/tmp`:
```bash
python3 -m venv /tmp/venv-orders
/tmp/venv-orders/bin/pip install -r collector/requirements.txt

cp collector/config.example.yaml collector/config.yaml   # укажи свои ПУБЛИЧНЫЕ чаты

# разовая выгрузка истории («холодный старт»):
/tmp/venv-orders/bin/python collector/export_history.py --config collector/config.yaml --limit 200

# live-режим (читает новые сообщения по кругу):
/tmp/venv-orders/bin/python collector/collector.py --config collector/config.yaml
```
Первый запуск попросит код подтверждения Telegram — после этого создастся
файл сессии (в `TG_SESSION`).

### 3. n8n workflows
Импортируй в n8n оба файла: `workflows/classify.json` и `workflows/api.json`.
Настрой Credentials: Postgres и OpenAI-совместимый LLM (для classify), а также
переменную/секрет с `BOT_TOKEN` для валидации `initData` в `api.json`.
Активируй оба воркфлоу.

### 4. Mini-app (фронт)
```bash
cd miniapp
cp .env.example .env            # VITE_API_BASE = https://<n8n-host>/webhook
npm install
npm run build                   # прод-сборка в miniapp/dist
# npm run dev                   # локальная разработка
```
Задеплой `miniapp/dist` на HTTPS-хостинг (Vercel/Netlify) и укажи этот URL
в @BotFather как URL мини-аппа (кнопка Web App).

### 5. (Опционально) выделенный валидатор initData
Если не хочешь держать `BOT_TOKEN` в n8n, подними отдельный сервис
(`validator/`, только stdlib): `python -m src.app` слушает `VALIDATOR_PORT`.
По умолчанию **не нужен** — `api.json` валидирует `initData` сам.

---

## Верификация

```bash
# n8n JSON валиден
python3 -c "import json,glob;[json.load(open(f)) for f in glob.glob('workflows/*.json')];print('workflows OK')"

# collector + validator: юнит-тесты (Telegram замокан, сеть не нужна)
/tmp/venv-orders/bin/python -m pytest        # 43 passed

# miniapp
cd miniapp && npm install && npx tsc --noEmit && npm run build
```

Тесты покрывают: **префильтр** (ключевые/стоп-слова, длина), **дедуп**
(нормализация + одинаковый хеш для перепостов), **парсинг ответа ИИ**
(markdown-обёртки, мусор, приведение типов, fallback на `is_order=false`),
**пайплайн** (счётчики seen/filtered/duplicates/accepted) и **валидацию
initData** (корректная/битая подпись, просроченный `auth_date`).

---

## Модель данных (кратко)

- **`raw_messages`** — сырьё от collector-а. `text_hash` с `UNIQUE` → дедуп на
  уровне БД (`ON CONFLICT DO NOTHING`). Статусы `pending → done/skipped`.
- **`orders`** — результат ИИ: `service_type`, `summary`, `budget`, `urgency`,
  `languages`/`skills_required` (JSONB, есть GIN-индексы), `message_link`.
- **`users`** — `tg_id` + `settings` (JSONB): навыки, ключевые слова, языки,
  категории, `min_budget`.
- **`user_order_status`** — статус (`new/interested/hidden/responded`) и личная
  заметка на пару (пользователь, заказ).

---

## Чек-лист готовности

- [x] Collector: чтение публичных чатов, префильтр, дедуп, запись в `raw_messages`
- [x] Разовая выгрузка истории (`export_history.py`)
- [x] `workflows/classify.json` — валидный n8n JSON (Schedule → AI → parse → INSERT)
- [x] `workflows/api.json` — валидный n8n JSON (webhooks + валидация initData)
- [x] Mini-app: лента, настройки, карточка заказа (deep-link, статусы, заметка)
- [x] Схема БД `db/001_orders.sql`, промпт `prompts/order_classifier.txt`
- [x] `.env.example`, `.gitignore`
- [x] Юнит-тесты (43 passed), `tsc --noEmit` чистый, `npm run build` зелёный
- [ ] Демо-GIF (см. плейсхолдер выше)

---

## Стек

Python 3.9+ · Telethon · asyncpg · PostgreSQL · n8n · OpenAI-совместимый LLM ·
React 18 · Vite · TypeScript · `@twa-dev/sdk`.
