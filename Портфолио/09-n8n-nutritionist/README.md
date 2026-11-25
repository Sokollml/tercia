# 🥗 AI-ассистент нутрициолог для Telegram (n8n)

> ⚠️ **Честно:** это демо-проект для портфолио. Не медицинский сервис. Оценки калорий и БЖУ даёт LLM «на глаз» — они приблизительны и не заменяют консультацию специалиста и точный подсчёт по этикеткам.

![Схема воркфлоу](docs/schema.png)
<!-- 📷 Скрин-плейсхолдер: сюда положите скриншот схемы из редактора n8n (Telegram Trigger → Switch → AI Agent → Code → Postgres → Telegram). Файл: docs/schema.png -->

## Что делает

Пользователь пишет боту, что съел (текстом, RU/EN) → **AI Agent** оценивает калории и БЖУ и возвращает строгий JSON → запись сохраняется в **Postgres** → бот отвечает разбором приёма пищи.

Команды:
- `/today` — сводка за сегодня (приёмы пищи, ккал, БЖУ);
- `/week` — сводка за 7 дней (сумма, среднее ккал/день, БЖУ).

**Пример диалога:**

```
Вы:  овсянка на молоке 200 г и банан
Бот: 🍽 Разбор: Овсянка на молоке + банан
     🔥 320 ккал
     🥩 Б: 10 г  🧈 Ж: 7 г  🍞 У: 55 г
     📝 Стандартная порция овсянки 200 г и средний банан.
     ✅ Записано (1/30 сегодня)

Вы:  /today
Бот: 📅 Сегодня
     🍽 Приёмов пищи: 1
     🔥 320 ккал
     🥩 Б: 10 г  🧈 Ж: 7 г  🍞 У: 55 г
```

## Стек

- **n8n** (уже развёрнут на вашем VPS: Docker + Postgres) — свой n8n поднимать НЕ нужно;
- **Telegram Bot API** — интерфейс;
- **LLM** — OpenAI или совместимый API (по умолчанию `gpt-4o-mini`);
- **Postgres** — хранение записей (та же БД, что у n8n, или отдельная).

## Структура репозитория

```
09-n8n-nutritionist/
├── README.md                     # этот файл
├── workflows/
│   └── nutrition_bot.json        # экспорт воркфлоу для импорта в n8n
├── db/
│   └── 001_nutrition.sql         # таблицы users, entries + индексы
├── prompts/
│   └── nutrition.txt             # системный промпт AI Agent (справка)
└── docs/
    └── schema.png                # (положите сюда скрин схемы)
```

---

## Установка (пошагово)

### 1. Регистрация бота у @BotFather

1. Откройте в Telegram [@BotFather](https://t.me/BotFather).
2. Отправьте `/newbot`, задайте имя и username (должен оканчиваться на `bot`).
3. Скопируйте **HTTP API token** — понадобится для credential в n8n.
4. (Опц.) `/setcommands` → добавьте:
   ```
   today - Сводка за сегодня
   week - Сводка за неделю
   ```

### 2. Накат SQL в Postgres

Примените миграцию к вашей БД. Например, если Postgres крутится в Docker рядом с n8n:

```bash
# скопировать файл в контейнер и применить
docker cp db/001_nutrition.sql <postgres_container>:/tmp/001_nutrition.sql
docker exec -i <postgres_container> psql -U <db_user> -d <db_name> -f /tmp/001_nutrition.sql

# или напрямую через psql
psql "postgresql://<user>:<pass>@<host>:5432/<db>" -f db/001_nutrition.sql
```

Скрипт идемпотентный (`CREATE TABLE IF NOT EXISTS`), повторный запуск безопасен.

### 3. Создание credentials в n8n

В n8n → **Credentials** → **New**, создайте три штуки:

| Credential | Тип в n8n | Что ввести |
|---|---|---|
| **Telegram Nutrition Bot** | `Telegram API` | Access Token от @BotFather |
| **OpenAI Nutrition** | `OpenAI API` | API-ключ OpenAI (или Base URL + ключ совместимого провайдера) |
| **Postgres Nutrition** | `Postgres` | host / port / database / user / password вашей БД |

> Для OpenAI-совместимого провайдера (LM Studio, Together, OpenRouter, локальный шлюз и т.п.) укажите в credential кастомный **Base URL**.

### 4. Импорт воркфлоу

1. В n8n: **Workflows** → **Import from File** (или меню «⋮» → *Import from File…*).
2. Выберите `workflows/nutrition_bot.json`.
3. После импорта откройте каждую ноду с иконкой credential и **выберите созданные credentials** из списка:
   - Telegram Trigger, Reply Food, Reply Today, Reply Week → *Telegram Nutrition Bot*;
   - OpenAI Chat Model → *OpenAI Nutrition*;
   - Insert Entry, Select Today, Select Week → *Postgres Nutrition*.
   > В JSON стоят плейсхолдеры `REPLACE_..._CRED_ID` — n8n предложит привязать реальные credentials при первом открытии нод.
4. (Опц.) в **OpenAI Chat Model** проверьте модель (`gpt-4o-mini` по умолчанию).
5. Нажмите **Save**, затем переключатель **Active** — n8n сам зарегистрирует webhook у Telegram.

### 5. Проверка

Напишите боту `овсянка 200 г и банан`, затем `/today` и `/week`.

---

## Как устроен воркфлоу

```
Telegram Trigger
      │
      ▼
  Switch Command ── /today ─► Select Today (SQL) ─► Reply Today
      │         └─ /week ──► Select Week  (SQL) ─► Reply Week
      │
      └─ (обычный текст = еда) ─► AI Agent ─► Parse & Validate (Code) ─► Insert Entry (SQL) ─► Reply Food
                                    ▲
                          OpenAI Chat Model  (ai_languageModel)
```

- **Switch Command** — маршрутизирует по префиксу текста: `/today`, `/week`, иначе → ветка еды (fallback-выход).
- **AI Agent + OpenAI Chat Model** — просят LLM вернуть строгий JSON (промпт зашит в системное сообщение ноды; копия — в `prompts/nutrition.txt`).
- **Parse & Validate (Code)** — `try/catch` вокруг `JSON.parse`, срезает markdown-обёртки `\`\`\`json`, нормализует числа. **Если JSON мусорный — fallback-ответ** с просьбой переписать (запись в БД не делается, `valid=false`).
- **Insert Entry** — `INSERT` пользователя (upsert по `tg_user_id`) и записи одним запросом; **дневной лимит демо** (30 записей/день) проверяется прямо в SQL (`WHERE cnt.c < $limit`) и вставка не происходит при превышении.
- **Reply Food / Today / Week** — форматируют ответ с эмодзи.

### Дневной лимит для демо

Лимит `30` записей на пользователя в сутки задан в двух местах:
- константа `DAILY_LIMIT` в ноде **Parse & Validate** (передаётся в SQL);
- условие в SQL ноды **Insert Entry**.

Чтобы изменить — поправьте константу в Code-ноде (значение автоматически уходит в запрос).

---

## Чек-лист запуска

- [ ] Бот создан у @BotFather, токен сохранён
- [ ] Применён `db/001_nutrition.sql` (таблицы `users`, `entries`, индексы на месте)
- [ ] Созданы 3 credentials в n8n (Telegram, OpenAI, Postgres)
- [ ] Импортирован `workflows/nutrition_bot.json`
- [ ] Во всех нодах привязаны реальные credentials (нет `REPLACE_...`)
- [ ] Проверена модель в OpenAI Chat Model
- [ ] Workflow **сохранён** и переведён в **Active**
- [ ] Тест: сообщение с едой → пришёл разбор и запись в БД
- [ ] Тест: `/today` и `/week` → пришли сводки
- [ ] Тест: мусорное сообщение → аккуратный fallback-ответ

---

## Ограничения (честно)

- Оценки БЖУ/ккал приблизительны — это LLM, не база нутриентов.
- Нет редактирования/удаления записей, нет целей по калориям, нет графиков.
- Часовой пояс дат — серверный (`CURRENT_DATE` Postgres); для мультизонных пользователей нужна доработка.
- Дневной лимит — демо-защита от спама, а не биллинг.
