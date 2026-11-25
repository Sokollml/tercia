import { useState } from 'react';
import type { KeyboardEvent } from 'react';
import { Chip } from './Chip';

interface TagInputProps {
  label: string;
  placeholder?: string;
  values: string[];
  onChange: (values: string[]) => void;
}

/** Ввод произвольных тегов (навыки, ключевые слова). Enter/запятая — добавить. */
export function TagInput({ label, placeholder, values, onChange }: TagInputProps) {
  const [draft, setDraft] = useState('');

  function commit() {
    const tag = draft.trim().toLowerCase();
    if (tag && !values.includes(tag)) onChange([...values, tag]);
    setDraft('');
  }

  function onKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      commit();
    } else if (e.key === 'Backspace' && !draft && values.length) {
      onChange(values.slice(0, -1));
    }
  }

  function remove(tag: string) {
    onChange(values.filter((v) => v !== tag));
  }

  return (
    <div className="field">
      <label className="field__label">{label}</label>
      <div className="taginput">
        {values.map((v) => (
          <Chip key={v} tone="accent" onClick={() => remove(v)}>
            {v} <span className="taginput__x">×</span>
          </Chip>
        ))}
        <input
          className="taginput__input"
          value={draft}
          placeholder={placeholder}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKeyDown}
          onBlur={commit}
        />
      </div>
    </div>
  );
}
