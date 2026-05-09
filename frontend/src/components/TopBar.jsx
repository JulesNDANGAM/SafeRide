import { useI18n } from '../i18n/useI18n'

export default function TopBar({ view, setView }) {
  const { lang, setLanguage, t } = useI18n()

  // Admin is intentionally NOT exposed in the public nav.
  // It remains reachable via the URL hash `#admin` (see App.jsx routing).
  const tabs = [
    { id: 'passenger', label: t('nav_passenger') },
    { id: 'driver', label: t('nav_driver') },
    { id: 'premium', label: t('nav_premium') },
    { id: 'about', label: t('nav_about') },
  ]

  return (
    <header className="topbar">
      <div className="container topbar-inner">
        <div className="brand">
          <div className="brand-logo">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2l8 4v6c0 6-4 10-8 12-4-2-8-6-8-12V6l8-4z" />
              <path d="M9 12l2 2 4-4" />
            </svg>
          </div>
          <span>{t('brand')}</span>
        </div>

        <nav className="nav" aria-label="primary">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={view === tab.id ? 'active' : ''}
              onClick={() => setView(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        <div className="lang">
          <button className={lang === 'fr' ? 'active' : ''} onClick={() => setLanguage('fr')}>FR</button>
          <button className={lang === 'en' ? 'active' : ''} onClick={() => setLanguage('en')}>EN</button>
        </div>
      </div>
    </header>
  )
}
