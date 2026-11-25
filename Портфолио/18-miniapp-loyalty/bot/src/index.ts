import 'dotenv/config';
import { Bot, InlineKeyboard } from 'grammy';

/**
 * Loyalty bot launcher.
 *
 * This bot's only job is to be the door into the mini-app:
 *   - it sets the chat "menu button" to open the mini-app, and
 *   - on /start it sends an inline button that opens the mini-app.
 *
 * All loyalty logic lives in the mini-app + backend. The same app adapts to
 * the user's role (customer vs. cafe admin), so staff and guests use one bot.
 */

const BOT_TOKEN = requireEnv('BOT_TOKEN');
const MINIAPP_URL = requireEnv('MINIAPP_URL');

const bot = new Bot(BOT_TOKEN);

// Persistent menu button (the "≡" next to the message field) opens the app.
bot.api
  .setChatMenuButton({
    menu_button: {
      type: 'web_app',
      text: 'Моя карта',
      web_app: { url: MINIAPP_URL },
    },
  })
  .catch((err) => console.error('Failed to set menu button:', err));

bot.command('start', async (ctx) => {
  const keyboard = new InlineKeyboard().webApp('☕ Открыть карту лояльности', MINIAPP_URL);
  await ctx.reply(
    'Добро пожаловать! Собирайте штампы за каждый напиток и получайте награды.\n\n' +
      'Нажмите кнопку ниже, чтобы открыть свою карту лояльности.',
    { reply_markup: keyboard },
  );
});

bot.command('help', async (ctx) => {
  await ctx.reply(
    'Откройте карту через кнопку меню или команду /start.\n' +
      'Сотрудники кафе видят панель для начисления штампов автоматически.',
  );
});

bot.catch((err) => {
  console.error('Bot error:', err);
});

bot.start({
  onStart: (info) => console.log(`Bot @${info.username} started (long polling)`),
});

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    console.error(`Missing required environment variable: ${name}`);
    process.exit(1);
  }
  return value;
}
