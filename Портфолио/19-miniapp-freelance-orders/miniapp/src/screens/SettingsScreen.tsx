import { useState } from 'react';
import { TagInput } from '../components/TagInput';
import { Chip } from '../components/Chip';
import { saveSettings } from '../api';
import { serviceLabel } from '../format';
import { LANGUAGES, SERVICE_TYPES } from '../types';
import type { UserSettings } from '../types';

interface SettingsScreenProps {
  settings: UserSettings;
  onSaved: (settings: UserSettings) => void;
  haptic: (style?: 'light' | 'medium' | 'heavy') => void;
}

/**
 * «Мои настройки»: навыки/ключевые слова/языки/категории/мин. бюджет.
 * Эти же поля используются фильтром «Под меня» в ленте.
 */
export function SettingsScreen({ settings, onSaved, haptic }: SettingsScreenProps) {
  const [draft, setDraft] = useState<UserSettings>(settings);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<'idle' | 'ok' | 'error'>('idle');
  const [message, setMessage] = useState<string | null>(null);

  function patch(part: Partial<UserSettings>) {
    setDraft((d) => ({ ...d, ...part }));
    setStatus('idle');
  }

  function toggleService(type: string) {
    const has = draft.service_types.includes(type);
    patch({
      service_types: has
        ? draft.service_types.filter((t) => t !== type)
        : [...draft.service_types, type],
    });
  }

  function toggleLanguage(lang: string) {
    const has = draft.languages.includes(lang);
    patch({
      languages: has
        ? draft.languages.filter((l) => l !== lang)
        : [...draft.languages, lang],
    });
  }

  async function onSubmit() {
    setSaving(true);
    setStatus('idle');
    setMessage(null);
    try {
      const saved = await saveSettings(draft);
      setDraft(saved);
      onSaved(saved);
      setStatus('ok');
      setMessage('Настройки сохранены');
      haptic('medium');
    } catch (e) {
      setStatus('error');
      setMessage(e instanceof Error ? e.message : 'Не удалось сохранить');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="screen">
      <p className="screen__hint">
        По этим параметрам работает фильтр «Под меня» в ленте.
      </p>

      <TagInput
        label="Мои навыки"
        placeholder="figma, react…"
        values={draft.skills}
        onChange={(skills) => patch({ skills })}
      />

      <TagInput
        label="Ключевые слова"
        placeholder="лендинг, бот…"
        values={draft.keywords}
        onChange={(keywords) => patch({ keywords })}
      />

      <div className="field">
        <label className="field__label">Категории</label>
        <div className="chips">
          {SERVICE_TYPES.map((t) => (
            <Chip
              key={t}
              tone="accent"
              active={draft.service_types.includes(t)}
              onClick={() => toggleService(t)}
            >
              {serviceLabel(t)}
            </Chip>
          ))}
        </div>
      </div>

      <div className="field">
        <label className="field__label">Языки</label>
        <div className="chips">
          {LANGUAGES.map((l) => (
            <Chip
              key={l}
              tone="accent"
              active={draft.languages.includes(l)}
              onClick={() => toggleLanguage(l)}
            >
              {l.toUpperCase()}
            </Chip>
          ))}
        </div>
      </div>

      <div className="field">
        <label className="field__label" htmlFor="min_budget">
          Минимальный бюджет, ₽
        </label>
        <input
          id="min_budget"
          className="input"
          type="number"
          inputMode="numeric"
          min={0}
          step={1000}
          value={draft.min_budget ?? ''}
          placeholder="без ограничения"
          onChange={(e) =>
            patch({
              min_budget: e.target.value === '' ? null : Number(e.target.value),
            })
          }
        />
      </div>

      {message && (
        <div className={`notice ${status === 'error' ? 'notice--error' : 'notice--ok'}`}>
          {message}
        </div>
      )}

      <button
        type="button"
        className="btn btn--primary btn--block"
        disabled={saving}
        onClick={onSubmit}
      >
        {saving ? 'Сохранение…' : 'Сохранить'}
      </button>
    </div>
  );
}
