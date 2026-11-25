import 'dotenv/config';

/**
 * Минимальный бот-лаунчер БЕЗ внешних зависимостей (кроме dotenv).
 * Задача только одна — по команде /start прислать пользователю кнопку,
 * открывающую mini-app (web_app). Вся логика привычек живёт во фронте+бэке.
 *
 * Используется long polling через Bot API (fetch). Для продакшена можно
 * заменить на webhook или взять готовый фреймворк (grammy/telegraf) — здесь
 * намеренно минимализм.
 *
 * Переменные окружения (см. .env.example):
 *   BOT_TOKEN   — токен из @BotFather
 *   MINIAPP_URL — https-URL развёрнутого фронтенда (mini-app)
 */

const BOT_TOKEN = process.env.BOT_TOKEN;
const MINIAPP_URL = process.env.MINIAPP_URL;

if (!BOT_TOKEN) {
  console.error('BOT_TOKEN не задан. Скопируйте .env.example в .env.');
  process.exit(1);
}
if (!MINIAPP_URL || !MINIAPP_URL.startsWith('https://')) {
  console.error('MINIAPP_URL должен быть https-URL (требование Telegram для web_app).');
  process.exit(1);
}

const API = `https://api.telegram.org/bot${BOT_TOKEN}`;

async function call(method, payload) {
  const res = await fetch(`${API}/${method}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return res.json();
}

async function sendMenu(chatId) {
  await call('sendMessage', {
    chat_id: chatId,
    text: 'Привет! Это трекер привычек. Нажми кнопку ниже, чтобы открыть приложение 👇',
    reply_markup: {
      inline_keyboard: [
        [{ text: '🔥 Открыть трекер', web_app: { url: MINIAPP_URL } }],
      ],
    },
  });
}

async function main() {
  const me = await call('getMe', {});
  if (!me.ok) {
    console.error('Не удалось авторизоваться в Bot API:', me.description);
    process.exit(1);
  }
  console.log(`[bot] запущен как @${me.result.username}`);
  console.log(`[bot] mini-app: ${MINIAPP_URL}`);

  let offset = 0;
  // Бесконечный цикл long polling.
  // eslint-disable-next-line no-constant-condition
  while (true) {
    try {
      const upd = await call('getUpdates', { offset, timeout: 30 });
      if (!upd.ok) continue;
      for (const u of upd.result) {
        offset = u.update_id + 1;
        const msg = u.message;
        if (msg && msg.text) {
          await sendMenu(msg.chat.id);
        }
      }
    } catch (err) {
      console.error('[bot] ошибка polling:', err.message);
      await new Promise((r) => setTimeout(r, 3000));
    }
  }
}

main();
