import { useEffect, useMemo } from 'react';
import WebApp from '@twa-dev/sdk';

export interface TelegramApi {
  webApp: typeof WebApp;
  colorScheme: 'light' | 'dark';
  userName: string | null;
  openLink: (url: string) => void;
  haptic: (style?: 'light' | 'medium' | 'heavy') => void;
}

/**
 * Инициализация Telegram WebApp: ready(), expand(), тема.
 * Нативный UI: цвета/кнопки берём из клиента Telegram.
 */
export function useTelegram(): TelegramApi {
  useEffect(() => {
    WebApp.ready();
    WebApp.expand();
  }, []);

  return useMemo<TelegramApi>(() => {
    const user = WebApp.initDataUnsafe?.user;
    return {
      webApp: WebApp,
      colorScheme: (WebApp.colorScheme as 'light' | 'dark') || 'light',
      userName: user ? user.first_name || user.username || null : null,
      openLink: (url: string) => {
        // Ссылки t.me открываем внутри Telegram, внешние — в браузере.
        if (url.startsWith('https://t.me/') || url.startsWith('tg://')) {
          WebApp.openTelegramLink(url);
        } else {
          WebApp.openLink(url);
        }
      },
      haptic: (style = 'light') => {
        try {
          WebApp.HapticFeedback.impactOccurred(style);
        } catch {
          /* haptic может быть недоступен вне мобильного клиента */
        }
      },
    };
  }, []);
}
