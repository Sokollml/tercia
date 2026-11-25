import crypto from 'node:crypto';

/**
 * ─────────────────────────────────────────────────────────────────────────────
 *  ВАЛИДАЦИЯ Telegram WebApp initData
 * ─────────────────────────────────────────────────────────────────────────────
 *
 *  Когда пользователь открывает mini-app, Telegram передаёт строку `initData`
 *  (window.Telegram.WebApp.initData) — это URL-encoded query-string вида:
 *
 *      query_id=AAH...&user=%7B%22id%22%3A123...%7D&auth_date=1699999999&hash=abcdef...
 *
 *  Задача бэкенда — убедиться, что эти данные действительно выданы Telegram и
 *  не подделаны. Проверка построена на HMAC-SHA256 и описана в официальной
 *  документации Telegram (Mini Apps → Validating data received via the Mini App).
 *
 *  АЛГОРИТМ (важно соблюдать порядок):
 *
 *   1. Распарсить query-string в пары ключ=значение.
 *   2. Извлечь и УБРАТЬ из набора поле `hash` (это и есть подпись, её мы
 *      сверяем, а не подписываем).
 *   3. Сформировать `data_check_string`: все оставшиеся пары в виде "key=value",
 *      отсортированные по ключу в алфавитном порядке и склеенные символом \n.
 *   4. Вычислить секретный ключ:
 *          secret_key = HMAC_SHA256(key = "WebAppData", message = bot_token)
 *      ВНИМАНИЕ на порядок аргументов: строка "WebAppData" выступает КЛЮЧОМ
 *      HMAC, а токен бота — сообщением. Это частый источник ошибок.
 *   5. Вычислить подпись:
 *          computed_hash = HMAC_SHA256(key = secret_key, message = data_check_string)
 *      в hex-представлении.
 *   6. Сравнить computed_hash с полем `hash` из initData. Сравнение делаем
 *      constant-time (timingSafeEqual), чтобы не сливать информацию по таймингам.
 *   7. (Опционально) Проверить `auth_date` — что данные не слишком старые
 *      (защита от replay-атак).
 *
 *  ВАЖНО: значения в data_check_string берутся в ИСХОДНОМ (уже декодированном
 *  URLSearchParams) виде — то есть JSON поля `user` не переэкранируется. Мы
 *  используем URLSearchParams, который декодирует percent-encoding ровно один
 *  раз, что соответствует ожиданиям Telegram.
 */

export interface TelegramUser {
  id: number;
  first_name?: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  photo_url?: string;
  is_premium?: boolean;
}

export interface InitDataParsed {
  user: TelegramUser;
  authDate: number; // unix seconds
  queryId?: string;
  raw: Record<string, string>;
}

export type ValidateResult =
  | { ok: true; data: InitDataParsed }
  | { ok: false; error: string };

/**
 * Проверяет подпись initData и (опционально) её возраст.
 *
 * @param initData  сырая строка initData из Telegram.WebApp.initData
 * @param botToken  токен бота из @BotFather
 * @param maxAgeSec максимальный возраст auth_date в секундах; 0 — не проверять
 */
export function validateInitData(
  initData: string,
  botToken: string,
  maxAgeSec = 0
): ValidateResult {
  if (!initData || typeof initData !== 'string') {
    return { ok: false, error: 'initData отсутствует' };
  }
  if (!botToken) {
    return { ok: false, error: 'BOT_TOKEN не сконфигурирован' };
  }

  // 1. Парсим query-string. URLSearchParams декодирует percent-encoding.
  const params = new URLSearchParams(initData);

  // 2. Достаём подпись и убираем её из набора.
  const hash = params.get('hash');
  if (!hash) {
    return { ok: false, error: 'В initData нет поля hash' };
  }
  params.delete('hash');

  // 3. Собираем data_check_string: пары key=value, отсортированные по ключу,
  //    склеенные через \n.
  const pairs: string[] = [];
  for (const [key, value] of params.entries()) {
    pairs.push(`${key}=${value}`);
  }
  pairs.sort(); // лексикографическая сортировка строк "key=value" по ключу
  const dataCheckString = pairs.join('\n');

  // 4. secret_key = HMAC_SHA256("WebAppData", bot_token)
  //    (ключ = "WebAppData", сообщение = токен бота)
  const secretKey = crypto
    .createHmac('sha256', 'WebAppData')
    .update(botToken)
    .digest();

  // 5. computed_hash = HMAC_SHA256(secret_key, data_check_string) в hex
  const computedHash = crypto
    .createHmac('sha256', secretKey)
    .update(dataCheckString)
    .digest('hex');

  // 6. Constant-time сравнение. Буферы должны быть одной длины.
  const a = Buffer.from(computedHash, 'hex');
  const b = Buffer.from(hash, 'hex');
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) {
    return { ok: false, error: 'Неверная подпись initData (hash не совпал)' };
  }

  // 7. Проверка возраста (auth_date) — защита от повторного использования.
  const authDateStr = params.get('auth_date');
  const authDate = authDateStr ? Number(authDateStr) : 0;
  if (maxAgeSec > 0) {
    const nowSec = Math.floor(Date.now() / 1000);
    if (!authDate || nowSec - authDate > maxAgeSec) {
      return { ok: false, error: 'initData устарел (auth_date просрочен)' };
    }
  }

  // Парсим пользователя.
  const userRaw = params.get('user');
  if (!userRaw) {
    return { ok: false, error: 'В initData нет поля user' };
  }
  let user: TelegramUser;
  try {
    user = JSON.parse(userRaw) as TelegramUser;
  } catch {
    return { ok: false, error: 'Поле user не является валидным JSON' };
  }
  if (!user || typeof user.id !== 'number') {
    return { ok: false, error: 'В user нет числового id' };
  }

  const raw: Record<string, string> = {};
  for (const [k, v] of new URLSearchParams(initData).entries()) raw[k] = v;

  return {
    ok: true,
    data: {
      user,
      authDate,
      queryId: params.get('query_id') ?? undefined,
      raw,
    },
  };
}

/**
 * ХЕЛПЕР ДЛЯ ТЕСТОВ / инструментов: собирает КОРРЕКТНО подписанную строку
 * initData из объекта полей. Используем ровно тот же алгоритм подписи, что и
 * Telegram, поэтому такую строку validateInitData() признаёт валидной.
 *
 * НЕ используется в рантайме сервера — только для генерации тестовых данных.
 */
export function signInitData(
  fields: Record<string, string>,
  botToken: string
): string {
  const params = new URLSearchParams();
  const pairs: string[] = [];
  for (const key of Object.keys(fields)) {
    params.set(key, fields[key]);
    pairs.push(`${key}=${fields[key]}`);
  }
  pairs.sort();
  const dataCheckString = pairs.join('\n');

  const secretKey = crypto
    .createHmac('sha256', 'WebAppData')
    .update(botToken)
    .digest();
  const hash = crypto
    .createHmac('sha256', secretKey)
    .update(dataCheckString)
    .digest('hex');

  params.set('hash', hash);
  return params.toString();
}
