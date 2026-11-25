import { useLang } from '../i18n/LanguageContext'

interface LangToggleProps {
  /** Tailwind classes for the wrapper. */
  className?: string
  /** Classes applied to the active language. */
  activeClassName?: string
  /** Classes applied to the inactive language. */
  inactiveClassName?: string
}

/**
 * Compact RU / EN switch. Presentation is delegated to the caller through
 * className props so every landing can theme it to match its own style.
 */
export default function LangToggle({
  className = '',
  activeClassName = 'opacity-100',
  inactiveClassName = 'opacity-40',
}: LangToggleProps) {
  const { lang, setLang } = useLang()
  return (
    <div className={`inline-flex items-center gap-1 text-xs font-semibold uppercase tracking-widest ${className}`} role="group" aria-label="Language / Язык">
      <button
        type="button"
        onClick={() => setLang('ru')}
        aria-pressed={lang === 'ru'}
        className={`transition-opacity ${lang === 'ru' ? activeClassName : inactiveClassName}`}
      >
        RU
      </button>
      <span aria-hidden="true" className="opacity-30">/</span>
      <button
        type="button"
        onClick={() => setLang('en')}
        aria-pressed={lang === 'en'}
        className={`transition-opacity ${lang === 'en' ? activeClassName : inactiveClassName}`}
      >
        EN
      </button>
    </div>
  )
}
