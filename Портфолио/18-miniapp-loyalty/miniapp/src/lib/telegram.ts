import WebApp from '@twa-dev/sdk';

/**
 * Thin wrapper around the Telegram WebApp SDK.
 *
 * Everything Telegram-specific lives here so the React components stay clean
 * and so the app degrades gracefully when opened outside Telegram (e.g. in a
 * plain browser during development), where `initData` is empty.
 */

let initialised = false;

export function initTelegram(): void {
  if (initialised) return;
  initialised = true;
  try {
    WebApp.ready();
    WebApp.expand();
    // Follow the user's Telegram theme for header/background.
    WebApp.setHeaderColor('secondary_bg_color');
  } catch {
    /* Not running inside Telegram — fine for local dev. */
  }
}

/** The signed initData string that authenticates every backend request. */
export function getInitData(): string {
  try {
    return WebApp.initData ?? '';
  } catch {
    return '';
  }
}

export function haptic(type: 'success' | 'error' | 'warning'): void {
  try {
    WebApp.HapticFeedback.notificationOccurred(type);
  } catch {
    /* no-op outside Telegram */
  }
}

export function impact(style: 'light' | 'medium' | 'heavy' = 'light'): void {
  try {
    WebApp.HapticFeedback.impactOccurred(style);
  } catch {
    /* no-op */
  }
}

/**
 * Open Telegram's NATIVE QR scanner popup and resolve with the scanned text.
 * Resolves with null if the user closes the scanner. Rejects if the running
 * client is too old to support the native scanner.
 */
export function scanQr(text = 'Наведите на QR-код гостя'): Promise<string | null> {
  return new Promise((resolve, reject) => {
    try {
      let settled = false;
      WebApp.showScanQrPopup({ text }, (data: string) => {
        if (settled) return true;
        settled = true;
        WebApp.closeScanQrPopup();
        resolve(data && data.length > 0 ? data : null);
        return true; // close the popup
      });
    } catch (err) {
      reject(err instanceof Error ? err : new Error('scanner_unavailable'));
    }
  });
}

export function showAlert(message: string): void {
  try {
    WebApp.showAlert(message);
  } catch {
    // eslint-disable-next-line no-alert
    alert(message);
  }
}

export { WebApp };
