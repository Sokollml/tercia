import crypto from 'node:crypto';

/**
 * Telegram WebApp initData validation.
 *
 * The mini-app receives a signed `initData` string from the Telegram client
 * (window.Telegram.WebApp.initData). We MUST verify it server-side before
 * trusting any user identity, otherwise anyone could forge a request claiming
 * to be an admin.
 *
 * Algorithm (per https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app):
 *
 *   1. Parse initData as a query string into key/value pairs.
 *   2. Remove the `hash` field — it is the signature to check against.
 *   3. Build the "data check string": every remaining pair formatted as
 *      `key=value`, sorted alphabetically by key, joined with a newline "\n".
 *   4. Derive the secret key:
 *          secret_key = HMAC_SHA256(key="WebAppData", message=bot_token)
 *      i.e. an HMAC-SHA256 where the *key* is the literal string "WebAppData"
 *      and the *message* is the bot token.
 *   5. Compute HMAC_SHA256(key=secret_key, message=data_check_string) as hex.
 *   6. Compare it, in constant time, with the `hash` from step 2.
 *
 * We also enforce a freshness window on `auth_date` to blunt replay attacks.
 */

export interface TelegramUser {
  id: number;
  first_name?: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
  photo_url?: string;
}

export type ValidationResult =
  | { ok: true; user: TelegramUser; authDate: number }
  | { ok: false; reason: string };

/**
 * Validate a raw initData string against a bot token.
 *
 * @param initData  the raw querystring from Telegram.WebApp.initData
 * @param botToken  the bot token (kept secret, server-side only)
 * @param maxAgeSeconds  reject initData whose auth_date is older than this
 */
export function validateInitData(
  initData: string,
  botToken: string,
  maxAgeSeconds = 86400,
): ValidationResult {
  if (!initData || typeof initData !== 'string') {
    return { ok: false, reason: 'empty_init_data' };
  }

  const params = new URLSearchParams(initData);

  const hash = params.get('hash');
  if (!hash) {
    return { ok: false, reason: 'missing_hash' };
  }

  // Step 2 + 3: everything except `hash`, sorted, joined by "\n".
  const pairs: string[] = [];
  for (const [key, value] of params.entries()) {
    if (key === 'hash') continue;
    pairs.push(`${key}=${value}`);
  }
  pairs.sort();
  const dataCheckString = pairs.join('\n');

  // Step 4: secret_key = HMAC_SHA256(key="WebAppData", message=bot_token)
  const secretKey = crypto
    .createHmac('sha256', 'WebAppData')
    .update(botToken)
    .digest();

  // Step 5: computed = HMAC_SHA256(key=secret_key, message=data_check_string)
  const computedHash = crypto
    .createHmac('sha256', secretKey)
    .update(dataCheckString)
    .digest('hex');

  // Step 6: constant-time comparison to avoid timing side-channels.
  const computedBuf = Buffer.from(computedHash, 'hex');
  const providedBuf = Buffer.from(hash, 'hex');
  if (
    computedBuf.length !== providedBuf.length ||
    !crypto.timingSafeEqual(computedBuf, providedBuf)
  ) {
    return { ok: false, reason: 'bad_hash' };
  }

  // Freshness check — protects against replaying an old, valid initData.
  const authDateRaw = params.get('auth_date');
  const authDate = authDateRaw ? Number(authDateRaw) : 0;
  if (!authDate || Number.isNaN(authDate)) {
    return { ok: false, reason: 'missing_auth_date' };
  }
  const nowSeconds = Math.floor(Date.now() / 1000);
  if (maxAgeSeconds > 0 && nowSeconds - authDate > maxAgeSeconds) {
    return { ok: false, reason: 'expired' };
  }

  // Parse the user payload (JSON-encoded inside the `user` field).
  const userRaw = params.get('user');
  if (!userRaw) {
    return { ok: false, reason: 'missing_user' };
  }
  let user: TelegramUser;
  try {
    user = JSON.parse(userRaw) as TelegramUser;
  } catch {
    return { ok: false, reason: 'bad_user_json' };
  }
  if (!user || typeof user.id !== 'number') {
    return { ok: false, reason: 'bad_user' };
  }

  return { ok: true, user, authDate };
}
