import crypto from 'node:crypto';
import { describe, expect, it } from 'vitest';
import { validateInitData } from '../src/lib/telegram.js';

/**
 * Build a correctly-signed initData string the way the Telegram client would,
 * so we can assert the validator accepts genuine data and rejects tampered data.
 */
function signInitData(
  botToken: string,
  fields: Record<string, string>,
): string {
  const dataCheckString = Object.keys(fields)
    .sort()
    .map((k) => `${k}=${fields[k]}`)
    .join('\n');
  const secretKey = crypto
    .createHmac('sha256', 'WebAppData')
    .update(botToken)
    .digest();
  const hash = crypto
    .createHmac('sha256', secretKey)
    .update(dataCheckString)
    .digest('hex');

  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(fields)) params.set(k, v);
  params.set('hash', hash);
  return params.toString();
}

const BOT_TOKEN = '123456:TEST_TOKEN_do_not_use';

function freshFields(overrides: Record<string, string> = {}) {
  return {
    user: JSON.stringify({ id: 42, first_name: 'Ann', username: 'ann' }),
    auth_date: String(Math.floor(Date.now() / 1000)),
    query_id: 'AAABBB',
    ...overrides,
  };
}

describe('validateInitData', () => {
  it('accepts a genuinely signed payload and returns the user', () => {
    const initData = signInitData(BOT_TOKEN, freshFields());
    const res = validateInitData(initData, BOT_TOKEN);
    expect(res.ok).toBe(true);
    if (res.ok) {
      expect(res.user.id).toBe(42);
      expect(res.user.username).toBe('ann');
    }
  });

  it('rejects when the signature was made with a different token', () => {
    const initData = signInitData('wrong-token', freshFields());
    const res = validateInitData(initData, BOT_TOKEN);
    expect(res.ok).toBe(false);
    if (!res.ok) expect(res.reason).toBe('bad_hash');
  });

  it('rejects tampered data (id changed after signing)', () => {
    const fields = freshFields();
    const initData = signInitData(BOT_TOKEN, fields);
    // Swap the signed user for a forged "admin" id, keep the old hash.
    const forged = initData.replace(
      encodeURIComponent(fields.user),
      encodeURIComponent(JSON.stringify({ id: 999999, first_name: 'Hax' })),
    );
    const res = validateInitData(forged, BOT_TOKEN);
    expect(res.ok).toBe(false);
  });

  it('rejects an expired payload', () => {
    const old = String(Math.floor(Date.now() / 1000) - 10_000);
    const initData = signInitData(BOT_TOKEN, freshFields({ auth_date: old }));
    const res = validateInitData(initData, BOT_TOKEN, 3600);
    expect(res.ok).toBe(false);
    if (!res.ok) expect(res.reason).toBe('expired');
  });

  it('rejects empty input and a missing hash', () => {
    expect(validateInitData('', BOT_TOKEN).ok).toBe(false);
    expect(validateInitData('user=%7B%7D&auth_date=1', BOT_TOKEN).ok).toBe(false);
  });
});
