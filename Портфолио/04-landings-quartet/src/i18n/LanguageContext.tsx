import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'

export type Lang = 'ru' | 'en'

interface LanguageContextValue {
  lang: Lang
  setLang: (lang: Lang) => void
  toggle: () => void
}

const LanguageContext = createContext<LanguageContextValue | null>(null)

const STORAGE_KEY = 'quartet-lang'

function readInitialLang(): Lang {
  if (typeof window === 'undefined') return 'ru'
  const stored = window.localStorage.getItem(STORAGE_KEY)
  if (stored === 'ru' || stored === 'en') return stored
  const nav = window.navigator.language.toLowerCase()
  return nav.startsWith('ru') ? 'ru' : 'en'
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(readInitialLang)

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, lang)
    document.documentElement.lang = lang
  }, [lang])

  const value = useMemo<LanguageContextValue>(
    () => ({
      lang,
      setLang: setLangState,
      toggle: () => setLangState((prev) => (prev === 'ru' ? 'en' : 'ru')),
    }),
    [lang],
  )

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}

export function useLang() {
  const ctx = useContext(LanguageContext)
  if (!ctx) throw new Error('useLang must be used within LanguageProvider')
  return ctx
}

/** Helper: pick the value for the current language from a { ru, en } record. */
export function useT<T>(dict: { ru: T; en: T }): T {
  const { lang } = useLang()
  return dict[lang]
}
