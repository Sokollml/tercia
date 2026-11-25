import { describe, it, expect } from 'vitest';
import { validateInitData, signInitData } from '../src/auth/initData.js';

const BOT_TOKEN = '123456:TEST_TOKEN_abcdefghijklmnopqrstuvwxyz';

function makeInitData(overrides: Record<string, string> = {}, token = BOT_TOKEN) {
  const authDate = Math.floor(Date.now() / 1000).toString();
  const fields: Record<string, string> = {
    query_id: 'AAHdF6IQAAAAAN0XohDhrOrc',
    user: JSON.stringify({ id: 42, first_name: 'Тест', username: 'tester' }),
    auth_date: authDate,
    ...overrides,
  };
  return signInitData(fields, token);
}

describe('validateInitData', () => {
  it('пропускает корректно подписанную строку', () => {
    const initData = makeInitData();
    const res = validateInitData(initData, BOT_TOKEN);
    expect(res.ok).toBe(true);
    if (res.ok) {
      expect(res.data.user.id).toBe(42);
      expect(res.data.user.username).toBe('tester');
    }
  });

  it('отклоняет подделанные данные (изменили user после подписи)', () => {
    const initData = makeInitData();
    // Подменяем user, не пересчитывая hash — подпись должна перестать сходиться.
    const params = new URLSearchParams(initData);
    params.set('user', JSON.stringify({ id: 999, first_name: 'Хакер' }));
    const tampered = params.toString();

    const res = validateInitData(tampered, BOT_TOKEN);
    expect(res.ok).toBe(false);
  });

  it('отклоняет строку, подписанную ЧУЖИМ токеном', () => {
    const initData = makeInitData({}, 'WRONG:another_bot_token');
    const res = validateInitData(initData, BOT_TOKEN);
    expect(res.ok).toBe(false);
  });

  it('отклоняет, если поля hash нет', () => {
    const res = validateInitData('user=%7B%22id%22%3A1%7D&auth_date=1', BOT_TOKEN);
    expect(res.ok).toBe(false);
  });

  it('отклоняет просроченный auth_date при maxAge', () => {
    const old = (Math.floor(Date.now() / 1000) - 100000).toString();
    const initData = makeInitData({ auth_date: old });
    const res = validateInitData(initData, BOT_TOKEN, 3600);
    expect(res.ok).toBe(false);
  });

  it('пропускает свежий auth_date при maxAge', () => {
    const initData = makeInitData();
    const res = validateInitData(initData, BOT_TOKEN, 3600);
    expect(res.ok).toBe(true);
  });
});
