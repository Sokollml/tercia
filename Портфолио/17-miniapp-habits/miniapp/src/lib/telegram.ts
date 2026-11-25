import WebApp from '@twa-dev/sdk';

/**
 * Обёртки над Telegram WebApp SDK: инициализация, применение темы к CSS-переменным,
 * тактильная отдача, управление MainButton/BackButton. Всё безопасно вызывается и
 * вне Telegram (в обычном браузере при разработке SDK подставляет заглушки).
 */

export { WebApp };

/** Готовим mini-app: сообщаем Telegram о готовности, разворачиваем на весь экран. */
export function initTelegram(): void {
  try {
    WebApp.ready();
    WebApp.expand();
    // Цвет шапки/фона под тему Telegram.
    WebApp.setHeaderColor('secondary_bg_color');
    applyTheme();
    WebApp.onEvent('themeChanged', applyTheme);
  } catch {
    // В обычном браузере часть методов может быть недоступна — не критично.
  }
}

/** Прокидывает themeParams Telegram в CSS-переменные :root (--tg-...). */
export function applyTheme(): void {
  const tp = WebApp.themeParams || {};
  const root = document.documentElement;
  const map: Record<string, string | undefined> = {
    '--tg-bg': tp.bg_color,
    '--tg-text': tp.text_color,
    '--tg-hint': tp.hint_color,
    '--tg-link': tp.link_color,
    '--tg-button': tp.button_color,
    '--tg-button-text': tp.button_text_color,
    '--tg-secondary-bg': tp.secondary_bg_color,
  };
  for (const [key, val] of Object.entries(map)) {
    if (val) root.style.setProperty(key, val);
  }
  root.dataset.tgTheme = WebApp.colorScheme || 'light';
}

/** initData для авторизации на бэке. В браузере вне Telegram будет пустой строкой. */
export function getInitData(): string {
  try {
    return WebApp.initData || '';
  } catch {
    return '';
  }
}

// ── Тактильная отдача ────────────────────────────────────────────────────────
export function hapticImpact(style: 'light' | 'medium' | 'heavy' = 'light'): void {
  try {
    WebApp.HapticFeedback.impactOccurred(style);
  } catch {
    /* no-op */
  }
}

export function hapticNotification(type: 'success' | 'warning' | 'error'): void {
  try {
    WebApp.HapticFeedback.notificationOccurred(type);
  } catch {
    /* no-op */
  }
}

// ── MainButton ───────────────────────────────────────────────────────────────
export function showMainButton(text: string, onClick: () => void): void {
  try {
    const mb = WebApp.MainButton;
    mb.setText(text);
    mb.offClick(onClick);
    mb.onClick(onClick);
    mb.show();
    mb.enable();
  } catch {
    /* no-op */
  }
}

export function hideMainButton(): void {
  try {
    WebApp.MainButton.hide();
  } catch {
    /* no-op */
  }
}

export function setMainButtonLoading(loading: boolean): void {
  try {
    if (loading) WebApp.MainButton.showProgress();
    else WebApp.MainButton.hideProgress();
  } catch {
    /* no-op */
  }
}

// ── BackButton ───────────────────────────────────────────────────────────────
export function showBackButton(onClick: () => void): void {
  try {
    const bb = WebApp.BackButton;
    bb.offClick(onClick);
    bb.onClick(onClick);
    bb.show();
  } catch {
    /* no-op */
  }
}

export function hideBackButton(): void {
  try {
    WebApp.BackButton.hide();
  } catch {
    /* no-op */
  }
}
