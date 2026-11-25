# 20 · n8n Lead Pipeline — обработка заявок с сайта

> **Честно: это демо-проект (портфолио).** Готовые к импорту файлы n8n, SQL и промпты.
> Файлы валидны и импортируются, но перед боевым запуском нужно подставить свои
> credentials, секретный токен и проверить окружение. Свой n8n поднимать не нужно —
> предполагается уже работающий n8n на VPS (Docker + Postgres).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  [ СКРИНШОТ СХЕМЫ n8n — ПЛЕЙСХОЛДЕР ]                                          │
│                                                                               │
│  Форма сайта ──POST──▶ Webhook ──▶ IF(токен) ──▶ Нормализация ──▶ AI Агент    │
│                                                     (классиф.)   │            │
│                                                                  ▼            │
│              Telegram ◀── IF(спам?) ◀── Postgres INSERT ◀── Парсинг+валидация │
│                 ▲               │            (ON CONFLICT DO NOTHING)          │
│              владелец      спам ▶ только лог                                   │
│                                                                               │
│  Расписание 09:00 МСК ──▶ Postgres SELECT(за день) ──▶ AI сводка ──▶ Telegram │
└─────────────────────────────────────────────────────────────────────────────┘
```
_Заменить блок выше на реальный скриншот схемы после импорта: `docs/schema.png`._

---

## Структура проекта

```
20-n8n-lead-pipeline/
├── workflows/
│   ├── lead_intake.json     # приём заявки: вебхук → ИИ → Postgres → Telegram
│   └── daily_digest.json    # сводка по расписанию 09:00 МСК
├── db/
│   └── 001_leads.sql        # таблицы leads (hash UNIQUE) + notifications + индексы
├── prompts/
│   ├── lead_classifier.txt  # промпт классификатора (RU/EN)
│   └── daily_digest.txt     # промпт сводки (RU/EN)
└── README.md
```

## Что делает пайплайн

**`lead_intake` (10 нод):**
1. **Вебхук: Заявка** — `POST /webhook/lead-intake`, принимает JSON формы.
2. **IF: Проверка токена** — сверяет заголовок `X-Webhook-Token` с секретом `$env.LEAD_WEBHOOK_TOKEN`. Не совпало → заявка молча отбрасывается.
3. **Код: Нормализация** — приводит поля (`name/contact/message/source`), считает детерминированный `hash` заявки (чистый JS, FNV-1a — без зависимости от системного `crypto`).
4. **AI Агент: Классификация** (+ **OpenAI Модель** через `ai_languageModel`) — строгий JSON: `type` (lead/question/spam), `name`, `contact`, `summary`, `budget`.
5. **Код: Парсинг JSON** — вытаскивает и валидирует JSON модели; при мусоре → `type='manual_review'`, флаг `fallback=true` (поток не падает).
6. **Postgres: INSERT лид** — `INSERT ... ON CONFLICT (hash) DO NOTHING RETURNING *`. Повторная заявка с тем же хешем **не создаёт дубль и не уведомляет второй раз** (на конфликте `RETURNING` пуст → поток дальше не идёт).
7. **IF: Спам?** — `is_spam = true` → **Код: Лог спама** (только запись в лог, без уведомления); иначе → **Telegram: Карточка** владельцу.

**`daily_digest` (5 нод):** Расписание 09:00 Europe/Moscow → `SELECT` заявок за сегодня → AI-сводка → Telegram владельцу.

## Модель данных (`db/001_leads.sql`)

- **`leads`** — `id`, `hash` (UNIQUE, идемпотентность), `type`, `name`, `contact`, `summary`, `budget`, `source`, `raw_message`, `is_spam`, `fallback`, `received_at`, `created_at`. Индексы по `received_at`, `type`, `is_spam`.
- **`notifications`** — журнал отправленных уведомлений (`lead_id`, `channel`, `status`, `payload jsonb`).

---

## Пошаговый запуск

### 1. Накат SQL
```bash
# через переменную окружения с DSN Postgres
psql "$DATABASE_URL" -f db/001_leads.sql

# или внутри Docker-compose (имя сервиса postgres — подставьте своё)
docker compose exec -T postgres psql -U n8n -d n8n < db/001_leads.sql
```
Скрипт идемпотентен (`CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`) — можно гонять повторно.

### 2. Импорт воркфлоу
В UI n8n: **Workflows → ⋯ (три точки) → Import from File** → выбрать `workflows/lead_intake.json`, затем `workflows/daily_digest.json`.
После импорта n8n попросит **сопоставить credentials** (см. ниже) — узлы помечены плейсхолдерами `REPLACE_..._CRED_ID`.

### 3. Credentials (создать в n8n → Credentials)
| Что | Тип credential в n8n | Где используется |
|-----|----------------------|------------------|
| **Postgres VPS** | `Postgres` | нода `Postgres: INSERT лид`, `Postgres: Заявки за день` |
| **Telegram Bot** | `Telegram API` (token от @BotFather) | ноды `Telegram: Карточка`, `Telegram: Сводка` |
| **OpenAI account** | `OpenAI API` | ноды `OpenAI Модель` в обоих воркфлоу |

После создания — в каждой соответствующей ноде выбрать нужный credential из списка.
> LLM можно заменить: удалить `OpenAI Модель` и подключить любую другую chat-модель n8n к входу `ai_languageModel` агента.

### 4. Переменные окружения (секреты — НЕ в JSON)
Добавьте в окружение n8n (`docker-compose.yml → environment` или `.env`):
```env
LEAD_WEBHOOK_TOKEN=длинная-случайная-строка   # секрет вебхука
OWNER_TELEGRAM_CHAT_ID=123456789               # chat_id владельца
```
После правки — перезапуск контейнера n8n. Значения читаются в нодах как `{{ $env.LEAD_WEBHOOK_TOKEN }}` и `{{ $env.OWNER_TELEGRAM_CHAT_ID }}`.

> **Где задать секретный токен вебхука:** переменная `LEAD_WEBHOOK_TOKEN` (см. выше).
> Проверка идёт в ноде **IF: Проверка токена**: заголовок запроса `X-Webhook-Token` должен точно совпасть с `LEAD_WEBHOOK_TOKEN`. На форме сайта отправляйте этот заголовок при POST-запросе.

### 5. Активация
Открыть `lead_intake` → **Active**. Скопировать **Production URL** вебхука (вид `https://<ваш-n8n>/webhook/lead-intake`). Активировать `daily_digest` для срабатывания расписания.

---

## Тест `curl`

Валидная заявка (совпадающий токен):
```bash
curl -X POST "https://<ваш-n8n>/webhook/lead-intake" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Token: длинная-случайная-строка" \
  -d '{
    "name": "Иван Петров",
    "contact": "ivan@example.com",
    "message": "Нужен лендинг под запуск, бюджет ~150 000 ₽, когда сможете начать?",
    "source": "website"
  }'
```

Проверка идемпотентности — повторите тот же запрос: в `leads` останется **одна** строка, второго уведомления в Telegram **не будет**.

Спам (уйдёт только в лог, без уведомления):
```bash
curl -X POST "https://<ваш-n8n>/webhook/lead-intake" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Token: длинная-случайная-строка" \
  -d '{"name":"SEO","contact":"","message":"Куплю ссылки дёшево http://spam.example","source":"bot"}'
```

Неверный токен (заявка отбрасывается на IF):
```bash
curl -X POST "https://<ваш-n8n>/webhook/lead-intake" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Token: wrong" \
  -d '{"name":"x","message":"test"}'
```

## Проверка целостности JSON
```bash
python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('workflows/*.json')]; print('JSON OK')"
```

## Заметки / ограничения (честно)
- Хеш идемпотентности — FNV-1a на нормализованных полях; при желании замените на `crypto.sha256` (нужен `NODE_FUNCTION_ALLOW_BUILTIN=crypto` в окружении n8n).
- `typeVersion` нод указаны под актуальные версии; при другой версии n8n импорт может предложить миграцию узла — это нормально.
- ID credentials в JSON — плейсхолдеры; реальная привязка делается в UI при импорте.
- Запись в таблицу `notifications` в воркфлоу не подключена (задел на будущее) — таблица создаётся SQL-скриптом.
