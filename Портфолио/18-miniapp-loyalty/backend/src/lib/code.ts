import crypto from 'node:crypto';

/**
 * Human-friendly, collision-resistant loyalty-card codes.
 *
 * The code is what the customer's QR encodes and what a cashier can also
 * type in manually. We avoid ambiguous characters (0/O, 1/I/L) so it stays
 * readable when typed by hand.
 */

const ALPHABET = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';

/** Generate a code like "LOY-7F3K-9QD2". */
export function generateCardCode(): string {
  const groups = [randomGroup(4), randomGroup(4)];
  return `LOY-${groups[0]}-${groups[1]}`;
}

function randomGroup(length: number): string {
  const bytes = crypto.randomBytes(length);
  let out = '';
  for (let i = 0; i < length; i++) {
    out += ALPHABET[bytes[i] % ALPHABET.length];
  }
  return out;
}

/** Normalise user-typed codes (upper-case, trim) for lookup. */
export function normalizeCode(input: string): string {
  return input.trim().toUpperCase();
}
