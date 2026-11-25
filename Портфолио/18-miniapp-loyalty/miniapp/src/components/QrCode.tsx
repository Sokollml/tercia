import { useEffect, useRef } from 'react';
import QRCode from 'qrcode';

/**
 * Renders `value` as a QR code onto a <canvas>. The cashier's phone scans this
 * to identify the customer's card. Colours are read from CSS variables so the
 * code stays crisp in both light and dark Telegram themes.
 */
export function QrCode({ value, size = 220 }: { value: string; size?: number }) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    QRCode.toCanvas(canvas, value, {
      width: size,
      margin: 1,
      color: {
        dark: '#141414ff',
        light: '#ffffffff',
      },
      errorCorrectionLevel: 'M',
    }).catch(() => {
      /* ignore render errors (e.g. empty value) */
    });
  }, [value, size]);

  return <canvas ref={ref} className="qr-canvas" width={size} height={size} />;
}
