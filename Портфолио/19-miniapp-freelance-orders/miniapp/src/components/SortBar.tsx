import type { SortKey } from '../types';

interface SortBarProps {
  value: SortKey;
  onChange: (sort: SortKey) => void;
  onlyMatched: boolean;
  onToggleMatched: (v: boolean) => void;
}

const OPTIONS: { key: SortKey; label: string }[] = [
  { key: 'new', label: 'Новые' },
  { key: 'budget', label: 'Дороже' },
  { key: 'urgency', label: 'Срочные' },
];

export function SortBar({ value, onChange, onlyMatched, onToggleMatched }: SortBarProps) {
  return (
    <div className="sortbar">
      <div className="sortbar__segments">
        {OPTIONS.map((o) => (
          <button
            key={o.key}
            type="button"
            className={`segment ${value === o.key ? 'segment--active' : ''}`}
            onClick={() => onChange(o.key)}
          >
            {o.label}
          </button>
        ))}
      </div>
      <label className="sortbar__toggle">
        <input
          type="checkbox"
          checked={onlyMatched}
          onChange={(e) => onToggleMatched(e.target.checked)}
        />
        <span>Под меня</span>
      </label>
    </div>
  );
}
