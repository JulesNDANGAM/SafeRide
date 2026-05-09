import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { translations } from './translations'

const I18nContext = createContext(null)

export function I18nProvider({ children }) {
  const [lang, setLang] = useState(() => {
    const stored = typeof window !== 'undefined' ? window.localStorage.getItem('saferide.lang') : null
    if (stored === 'fr' || stored === 'en') return stored
    if (typeof navigator !== 'undefined' && navigator.language?.startsWith('fr')) return 'fr'
    return 'en'
  })

  const setLanguage = useCallback((next) => {
    setLang(next)
    try {
      window.localStorage.setItem('saferide.lang', next)
      document.documentElement.lang = next
    } catch (_) {}
  }, [])

  const t = useCallback(
    (key) => translations[lang]?.[key] ?? translations.en[key] ?? key,
    [lang],
  )

  const value = useMemo(() => ({ lang, setLanguage, t }), [lang, setLanguage, t])
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}

export function useI18n() {
  const ctx = useContext(I18nContext)
  if (!ctx) throw new Error('useI18n must be used inside I18nProvider')
  return ctx
}
