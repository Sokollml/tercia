# 11 — ИИ-ассистент поддержки / FAQ на n8n

> **Статус: демо-проект (портфолио).** Готовые к импорту файлы воркфлоу, SQL-схема
> и промпт. Реальные ключи (Telegram, LLM, Postgres) и chat id владельца/админа
> нужно подставить самостоятельно — это отмечено плейсхолдерами в файлах.

## Что делает

Клиент пишет боту в Telegram → бот ищет ответ в базе знаний (Postgres,
полнотекстовый поиск + нечёткий ILIKE) → **AI Agent формулирует ответ СТРОГО
на основе найденных записей** (ничего не выдумывает). Если релевантного ничего
не найдено — вопрос записывается в таблицу `unanswered`, владельцу уходит
уведомление, а клиент получает вежливый ответ, что вопрос передан специалисту.

Отдельный **админ-бот** позволяет пополнять базу и смотреть неотвеченные вопросы
(команды `/add`, `/unanswered`) с проверкой Telegram id администратора.

Языки: **RU / EN** — язык ответа подбирается под язык вопроса.

## Схема (плейсхолдер)

```
[ Скриншот схемы workflow — вставить после импорта в n8n ]

faq_bot.json:
  Telegram Trigger → Search FAQ (Postgres) → Prepare Context (Code) → Found? (IF)
        ├─ да  → AI Agent Answer ⇐ OpenAI Chat Model → Reply To Client (Telegram)
        └─ нет → Log Unanswered (Postgres) → Escalate To Owner (Telegram)
                                           → Reply Client (No Answer) (Telegram)

faq_admin.json:
  Admin Telegram Trigger → Parse Command (Code) → Is Admin? (IF)
        ├─ да  → Route Command (Switch)
        │         ├─ /add        → Insert FAQ (Postgres) → Confirm Added
        │         ├─ /unanswered → Get Unanswered (Postgres) → Format List → Send List
        │         └─ иначе       → Send Help
        └─ нет → Access Denied
```

## Структура проекта

```
11-n8n-faq-support/
├── workflows/
│   ├── faq_bot.json      # основной бот поддержки (клиентский)
│   └── faq_admin.json    # админ-бот пополнения базы
├── db/
│   └── 001_faq.sql       # таблицы faq + unanswered, индексы, демо-данные
├── prompts/
│   └── faq_answer.txt    # системный промпт AI Agent (RU/EN)
└── README.md
```

## Установка

Предполагается, что **n8n уже развёрнут** (Docker + Postgres на VPS).

### 1. База данных

Выполните SQL в вашей Postgres (той же или отдельной от служебной БД n8n):

```bash
psql "postgresql://USER:PASS@HOST:5432/DBNAME" -f db/001_faq.sql
```

Создаст таблицы `faq` (с GIN-индексом по `tsvector` и триграммными индексами)
и `unanswered`, плюс несколько демо-записей.

### 2. Импорт воркфлоу

В n8n: **Workflows → ⋯ (три точки) → Import from File** — импортируйте оба:
`workflows/faq_bot.json` и `workflows/faq_admin.json`.

### 3. Credentials

Настройте учётные данные и привяжите их к нодам:

| Тип credential                | Где взять                                   | В каких нодах |
|-------------------------------|---------------------------------------------|---------------|
| **Telegram API** (клиентский) | токен от @BotFather для бота поддержки       | Telegram Trigger, Reply To Client, Escalate To Owner, Reply Client (No Answer) в `faq_bot` |
| **Telegram API** (админский)  | токен от @BotFather для админ-бота (второй бот) | все Telegram-ноды в `faq_admin` |
| **OpenAI** (или другой LLM)   | API-ключ провайдера                          | OpenAI Chat Model в `faq_bot` |
| **Postgres**                  | доступ к БД с таблицами `faq` / `unanswered` | Search FAQ, Log Unanswered, Insert FAQ, Get Unanswered |

> Можно использовать любой чат-LLM: замените ноду `OpenAI Chat Model`
> на соответствующую (`lmChatOpenRouter`, `lmChatGroq` и т.д.), сохранив
> связь `ai_languageModel` к ноде `AI Agent Answer`.

### 4. @BotFather

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram.
2. `/newbot` → создайте **бота поддержки**, скопируйте токен → в Telegram credential для `faq_bot`.
3. `/newbot` ещё раз → создайте **админ-бота**, токен → в credential для `faq_admin`.
4. Свой Telegram id можно узнать через [@userinfobot](https://t.me/userinfobot).

### 5. Подставить плейсхолдеры

- `faq_bot.json` → нода **Escalate To Owner** → `chatId`: заменить
  `REPLACE_WITH_OWNER_CHAT_ID` на chat id владельца.
- `faq_admin.json` → нода **Parse Command** → в коде `const ADMIN_ID = 123456789;`
  заменить на ваш Telegram user id.

### 6. Активация

Включите оба воркфлоу тумблером **Active**. Telegram-триггеры сами
зарегистрируют webhook.

## Как работает поиск (без выдумок)

- Полнотекстовый поиск: `search_vector @@ plainto_tsquery('simple', $1)`
  с ранжированием `ts_rank`; конфигурация `simple` работает и для RU, и для EN.
- Нечёткий fallback по `ILIKE` (индексы `pg_trgm`) — ловит опечатки/частичные совпадения.
- Нода **Prepare Context** собирает найденные записи в один текстовый контекст.
- **AI Agent** получает системный промпт (`prompts/faq_answer.txt`): отвечать
  **только** на основе контекста; если ответа нет — честно сообщить.
- Если поиск не дал строк — ветка «нет»: запись в `unanswered` + эскалация.

## Чек-лист запуска

- [ ] Выполнен `db/001_faq.sql`, таблицы `faq` и `unanswered` созданы.
- [ ] Импортированы оба воркфлоу.
- [ ] Созданы 2 бота у @BotFather (поддержка + админ).
- [ ] Настроены credentials: 2× Telegram, LLM, Postgres.
- [ ] `REPLACE_WITH_OWNER_CHAT_ID` заменён на chat id владельца.
- [ ] `ADMIN_ID` в `Parse Command` заменён на ваш Telegram id.
- [ ] Оба воркфлоу переведены в **Active**.
- [ ] Тест: вопрос из демо-базы → бот отвечает по базе.
- [ ] Тест: незнакомый вопрос → запись в `unanswered` + уведомление владельцу.
- [ ] Тест: `/add Вопрос | Ответ` от админа → запись добавлена, отвечается.
- [ ] Тест: `/add` от постороннего → «Нет доступа».
- [ ] Тест: `/unanswered` → список неотвеченных.

## Ограничения (честно)

- Здесь поиск лексический (tsvector/ILIKE), без векторных эмбеддингов —
  для семантического поиска можно добавить pgvector + ноду эмбеддингов.
- SQL использует `queryReplacement` — для продакшена проверьте экранирование
  и лимиты длины сообщений Telegram (4096 символов).
- Ветка эскалации шлёт владельцу одно сообщение на вопрос; троттлинг/дедупликация
  не реализованы.
