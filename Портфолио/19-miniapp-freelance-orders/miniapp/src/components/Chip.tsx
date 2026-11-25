import type { ReactNode } from 'react';

interface ChipProps {
  children: ReactNode;
  active?: boolean;
  onClick?: () => void;
  tone?: 'default' | 'accent' | 'danger' | 'success';
}

export function Chip({ children, active, onClick, tone = 'default' }: ChipProps) {
  const cls = ['chip', active ? 'chip--active' : '', `chip--${tone}`]
    .filter(Boolean)
    .join(' ');
  if (onClick) {
    return (
      <button type="button" className={cls} onClick={onClick}>
        {children}
      </button>
    );
  }
  return <span className={cls}>{children}</span>;
}
