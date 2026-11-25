import type { Urgency } from './types';

const SERVICE_LABELS: Record<string, string> = {
  design: 'Дизайн',
  dev: 'Разработка',
  copywriting: 'Копирайтинг',
  smm: 'SMM',
  video: 'Видео',
  marketing: 'Маркетинг',
  audio: 'Аудио',
  '3d': '3D',
  other: 'Другое',
};

const URGENCY_LABELS: Record<Urgency, string> = {
  low: 'Не срочно',
  medium: 'Средне',
  high: 'Срочно',
};

export function serviceLabel(type: string | null): string {
  if (!type) return 'Без категории';
  return SERVICE_LABELS[type] || type;
}

export function urgencyLabel(u: Urgency): string {
  return URGENCY_LABELS[u];
}

export function formatBudget(budget: number | null): string {
  if (budget == null) return 'Бюджет не указан';
  return new Intl.NumberFormat('ru-RU').format(budget) + ' ₽';
}

export function timeAgo(iso: string): string {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return '';
  const diff = Math.max(0, Date.now() - then);
  const min = Math.floor(diff / 60000);
  if (min < 1) return 'только что';
  if (min < 60) return `${min} мин назад`;
  const hours = Math.floor(min / 60);
  if (hours < 24) return `${hours} ч назад`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days} дн назад`;
  return new Date(then).toLocaleDateString('ru-RU');
}
