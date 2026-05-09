import { useEffect, useState } from 'react'
import { api } from './api'
import { useI18n } from './i18n/useI18n'
import TopBar from './components/TopBar'
import PassengerView from './components/PassengerViewSimple'
import DriverView from './components/DriverView'
import AboutView from './components/AboutView'
import PremiumView from './components/PremiumView'
import AdminView from './components/AdminView'

function Hero({ onCta }) {
  const { t } = useI18n()
  return (
    <section className="container hero" style={{ padding: '40px 0' }}>
      <div style={{ textAlign: 'center', maxWidth: '800px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '36px', marginBottom: '16px', lineHeight: '1.3' }}>
          {t('hero_title_simple')}
        </h1>
        <p style={{ fontSize: '18px', color: '#94a3b8', marginBottom: '30px', lineHeight: '1.6' }}>
          {t('hero_desc_simple')}
        </p>
        <button 
          className="btn btn-primary" 
          onClick={() => onCta('passenger')}
          style={{ fontSize: '18px', padding: '16px 40px' }}
        >
          {t('cta_book_now')}
        </button>
      </div>
    </section>
  )
}

const PUBLIC_VIEWS = ['passenger', 'driver', 'premium', 'about']

function readViewFromHash() {
  const path = (window.location.pathname || '').replace(/^\/+|\/+$/g, '').toLowerCase()
  if (path === 'admin') return 'admin'
  const h = (window.location.hash || '').replace('#', '').trim().toLowerCase()
  if (h === 'admin') return 'admin'
  if (PUBLIC_VIEWS.includes(h)) return h
  return 'passenger'
}

export default function App() {
  const { t } = useI18n()
  const [view, setView] = useState(readViewFromHash)
  const [cities, setCities] = useState([])
  const [bootError, setBootError] = useState('')

  useEffect(() => {
    api.cities().then(setCities).catch((e) => setBootError(e.message))
  }, [])

  // Reflect view changes in the URL hash so admins can deep-link via #admin
  useEffect(() => {
    if (view === 'admin' && window.location.pathname.replace(/^\/+|\/+$/g, '').toLowerCase() === 'admin') {
      return
    }
    const target = `#${view}`
    if (window.location.hash !== target) {
      window.history.replaceState(null, '', target)
    }
  }, [view])

  // React to manual hash changes (e.g. user types #admin in the address bar)
  useEffect(() => {
    const onHash = () => setView(readViewFromHash())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  return (
    <div className="app">
      <TopBar view={view} setView={setView} />
      {view !== 'admin' && view !== 'passenger' && <Hero onCta={setView} />}

      {bootError && (
        <div className="container">
          <div className="error-banner">
            Backend unreachable: {bootError}. Run <span className="kbd">uvicorn app.main:app --reload --app-dir backend</span>
          </div>
        </div>
      )}

      {cities.length > 0 && view === 'passenger' && <PassengerView cities={cities} />}
      {cities.length > 0 && view === 'driver' && <DriverView cities={cities} />}
      {cities.length > 0 && view === 'premium' && <PremiumView cities={cities} />}
      {view === 'admin' && <AdminView cities={cities} />}
      {view === 'about' && <AboutView />}

      <footer className="footer">
        <div className="container">{t('footer')} · v1.0.0</div>
      </footer>
    </div>
  )
}
