# 21 — n8n: мониторинг источника + отчёт по расписанию

**Демо-проект** для портфолио: n8n по расписанию опрашивает публичный JSON-источник,
складывает нормализованный снапшот в PostgreSQL, сравнивает с прошлым прогоном и,
**только если есть изменения**, шлёт сводку в Telegram.

> Статус: демо. Логика рабочая, но перед продакшеном нужно завести реальные
> credentials, создать таблицы в БД и проверить лимиты источника.

---

## Схема workflow

```
[Schedule Trigger] → [Source Config (Set)] → [HTTP Request] → [Normalize Items (Code)]
        → [Load Previous Snapshot (Postgres)] → [Detect Changes (Code)]
              ├──→ [Persist Snapshot (Postgres)]        (выполняется всегда)
              └──→ [IF Has Changes] --true--> [Build Summary (Code)] → [Telegram Summary]
                                    --false--> (стоп, тишина)
```

*(скрин-плейсхолдер: сюда вставить скриншот канвы n8n после импорта — `docs/schema.png`)*

---

## Демо-источник (честно)

Используется публичный JSON API **Remotive — Remote Jobs**:

```
https://remotive.com/api/remote-jobs?limit=50
```

Это открытый демонстрационный источник вакансий (`{ "jobs": [ ... ] }`). Выбран потому,
что отдаёт стабильный JSON без ключа и без авторизации. Это **демо**: API — сторонний,
у него свои лимиты и ToS; для реального мониторинга подставьте свой источник (см. ниже).
Поле «зарплата» (`salary`) у вакансий часто пустое или строкой — в нормализации оно
приводится к числу либо `null`, поэтому детект «подешевело» срабатывает не по всем записям.

---

## Что внутри

| Файл | Назначение |
|------|-----------|
| `workflows/monitor.json` | Экспорт workflow n8n (импортируется целиком) |
| `db/001_monitor.sql` | Таблицы `monitor_items`, `monitor_snapshots` + индексы |
| `README.md` | Этот файл |

---

## Установка

### 1. База данных

Применить миграцию к вашему Postgres (можно в тот же, где живёт n8n, лучше в отдельную БД/схему):

```bash
psql "$DATABASE_URL" -f db/001_monitor.sql
```

Создаст:
- `monitor_items` — актуальное состояние записей (апсерт каждый прогон, пропавшие → `is_active = false`);
- `monitor_snapshots` — журнал изменений (история для отчётов).

### 2. Импорт workflow

В n8n: **Workflows → ⋮ (три точки) → Import from File** → выбрать `workflows/monitor.json`.

### 3. Credentials

После импорта у нод будут «пустые» ссылки на credentials — привязать вручную:

| Нода | Тип credential | Что нужно |
|------|----------------|-----------|
| `Load Previous Snapshot`, `Persist Snapshot` | **Postgres** | host, port, database, user, password вашей БД |
| `Telegram Summary` | **Telegram API** | Bot Token (создать бота у `@BotFather`) |
| `HTTP Request` | — | не требуется: источник публичный, без ключа |

Telegram chat id прокидывается через переменную окружения n8n **`TELEGRAM_CHAT_ID`**
(нода читает `{{ $env.TELEGRAM_CHAT_ID }}`). Задать в `docker-compose` сервиса n8n:

```yaml
environment:
  - TELEGRAM_CHAT_ID=123456789
```

Узнать свой chat id: написать боту, затем открыть
`https://api.telegram.org/bot<TOKEN>/getUpdates`.

> HTTP-credential понадобится, только если вы замените источник на API с ключом —
> тогда включите на ноде `HTTP Request` авторизацию (Header Auth / Query Auth).

### 4. Запуск

Открыть workflow, нажать **Execute Workflow** (ручной прогон для проверки), затем
активировать тумблером **Active**, чтобы работал по расписанию.

---

## Как заменить / добавить источник

Вся конфигурация источника вынесена в ноду **`Source Config` (Set)**:

- `sourceKey` — ключ источника (используется как раздел в БД, разные источники не пересекаются);
- `sourceUrl` — URL JSON API;
- `category` — произвольный доп. параметр (пример расширения).

**Заменить источник:**
1. Поменять `sourceUrl` и `sourceKey` в `Source Config`.
2. Поправить парсинг в ноде **`Normalize Items`**: там разбирается структура ответа
   (`raw.jobs`, поля `id/title/company_name/salary/url/publication_date`). Приведите её
   к единому item: `externalId, title, company, price, url, published_at, fingerprint`.
   Остальной pipeline (сравнение, БД, Telegram) менять не нужно — он работает с нормализованным форматом.

**Добавить второй источник:** проще всего дублировать workflow с другим `sourceKey`,
либо расширить `Source Config` до списка и обернуть HTTP+Normalize в цикл (Split In Batches).
Разделение по `source_key` в БД уже заложено.

---

## Расписание

Настраивается в ноде **`Schedule Trigger`**. Сейчас: **каждые 6 часов**.
Поменять интервал/крон можно прямо в ноде (поддерживает cron-выражения).

---

## Троттлинг и надёжность

- **Retry на сеть**: у ноды `HTTP Request` включён `retryOnFail` — до 4 попыток с паузой 5 сек
  (обрабатывает временные сетевые сбои / 5xx). Таймаут запроса 15 сек.
- **Троттлинг объёма**: и в URL (`limit=50`), и в `Normalize Items` (`MAX_ITEMS = 50`) —
  ограничивает нагрузку на источник и на БД за один прогон.
- **Дедуп**: внутри прогона — по `externalId` (Set в `Normalize Items`); в БД — уникальный
  индекс `(source_key, external_id)` + `ON CONFLICT DO UPDATE`.
- **Тишина без изменений**: `Persist Snapshot` обновляет БД всегда, но `IF Has Changes`
  пускает дальше к Telegram только при реальных изменениях — без спама.
- **Разумный интервал**: 6 часов — не долбим источник; при более частом опросе учитывайте его лимиты/ToS.

---

## Логика детекта изменений

Нода `Detect Changes` сравнивает текущий прогон с прошлым снапшотом (`is_active = true`):

- **новое** — `externalId` есть сейчас, но не было в БД;
- **изменилось** — сменился `fingerprint` (хэш значимых полей) → `updated`;
- **подешевело** — цена стала меньше прошлой → `price_drop` (частный случай изменения, подсвечивается отдельно);
- **пропало** — `externalId` был активен в БД, но отсутствует в текущем прогоне.

---

## Проверка валидности JSON

```bash
python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('workflows/*.json')]"
```
