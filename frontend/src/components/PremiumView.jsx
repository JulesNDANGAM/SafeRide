import { useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import { useI18n } from '../i18n/useI18n'

export default function PremiumView({ cities }) {
  const { t, lang } = useI18n()

  const [plans, setPlans] = useState([])
  const [city, setCity] = useState('Douala')
  const [drivers, setDrivers] = useState([])
  const [driverId, setDriverId] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [subscription, setSubscription] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [iframeLoaded, setIframeLoaded] = useState(false)

  const plan = useMemo(() => plans.find((p) => p.code === 'premium-driver') ?? plans[0], [plans])

  useEffect(() => {
    api.plans().then(setPlans).catch((e) => setError(e.message))
  }, [])

  useEffect(() => {
    api.drivers(city).then((data) => {
      setDrivers(data)
      setDriverId(data[0]?.driver?.id ?? '')
    }).catch((e) => setError(e.message))
  }, [city])

  // Poll subscription status while pending so admin webhook updates reflect here.
  useEffect(() => {
    if (!subscription || subscription.status !== 'pending') return undefined
    const id = setInterval(async () => {
      try {
        const fresh = await api.getSubscription(subscription.id)
        if (fresh.status !== subscription.status) setSubscription(fresh)
      } catch (_) {}
    }, 5000)
    return () => clearInterval(id)
  }, [subscription])

  async function simulatePayment() {
    if (!subscription) return
    try {
      const updated = await api.simulatePayment(subscription.id)
      setSubscription(updated)
    } catch (e) { setError(e.message) }
  }

  async function subscribe() {
    if (!driverId) return
    setLoading(true); setError(''); setIframeLoaded(false)
    try {
      const sub = await api.createSubscription({
        driver_id: driverId,
        plan_code: plan?.code ?? 'premium-driver',
        customer_email: email || null,
        customer_phone: phone || null,
      })
      setSubscription(sub)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  const features = plan ? (lang === 'fr' ? plan.features_fr : plan.features_en) : []
  const planLabel = plan ? (lang === 'fr' ? plan.label_fr : plan.label_en) : ''
  const statusLabel = subscription ? t(`premium_status_${subscription.status}`) : ''

  return (
    <div className="container section">
      <section className="grid-2">
        <div className="card">
          <span className="hero-eyebrow"><span style={{ width: 8, height: 8, borderRadius: 50, background: '#22c55e' }} /> Chariow</span>
          <h2 style={{ marginTop: 14 }}>{t('premium_title')}</h2>
          <p style={{ color: 'var(--muted)', marginTop: 8 }}>{t('premium_desc')}</p>

          {plan && (
            <div className="card tight" style={{ marginTop: 16, background: 'rgba(8,14,27,.55)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 10 }}>
                <h3>{planLabel}</h3>
                <div className="driver-score score-good">{plan.price_xaf.toLocaleString()} XAF</div>
              </div>
              <p style={{ color: 'var(--muted)', fontSize: '.85rem' }}>{t('premium_features')}</p>
              <ul style={{ listStyle: 'none', padding: 0, marginTop: 8, display: 'grid', gap: 6 }}>
                {features.map((f) => (
                  <li key={f} style={{ display: 'flex', gap: 8, alignItems: 'flex-start', fontSize: '.9rem' }}>
                    <span style={{ color: 'var(--accent-2)' }}>✓</span> {f}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="form-grid" style={{ marginTop: 16 }}>
            <label>
              <span>{t('city')}</span>
              <select value={city} onChange={(e) => setCity(e.target.value)}>
                {cities.map((c) => (<option key={c.code} value={c.code}>{c.label}</option>))}
              </select>
            </label>
            <label>
              <span>{t('premium_select_driver')}</span>
              <select value={driverId} onChange={(e) => setDriverId(e.target.value)}>
                {drivers.map((d) => (<option key={d.driver.id} value={d.driver.id}>{d.driver.name} · {d.driver.plate}</option>))}
              </select>
            </label>
            <label>
              <span>{t('premium_email')}</span>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="driver@example.com" />
            </label>
            <label>
              <span>{t('premium_phone')}</span>
              <input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+237..." />
            </label>
          </div>

          <div className="form-actions">
            <button className="btn btn-primary" onClick={subscribe} disabled={loading || !driverId}>
              {loading ? '...' : t('premium_subscribe')}
            </button>
            <span style={{ color: 'var(--muted)', fontSize: '.85rem', alignSelf: 'center' }}>
              {t('premium_secured_by')} <strong style={{ color: 'var(--accent)' }}>Chariow</strong>
            </span>
          </div>

          {error && <div className="error-banner">{error}</div>}
        </div>

        <div className="card">
          <h2>{t('premium_status')}</h2>
          {!subscription ? (
            <p style={{ color: 'var(--muted)', marginTop: 12 }}>{t('premium_iframe_help')}</p>
          ) : (
            <>
              <div className="signal-row" style={{ marginTop: 8 }}>
                <div>
                  <div className="sig-name">{subscription.id}</div>
                  <div className="sig-cat">{subscription.created_at}</div>
                </div>
                <div className="kbd">{subscription.price_xaf.toLocaleString()} XAF</div>
                <div className={`sig-score ${subscription.status === 'active' ? 'score-good' : subscription.status === 'pending' ? 'score-warn' : 'score-bad'}`}>
                  {statusLabel}
                </div>
              </div>

              {subscription.status === 'active' ? (
                <div className="card tight" style={{ marginTop: 14, borderColor: 'rgba(34,197,94,.4)', background: 'rgba(34,197,94,.08)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
                    <div style={{ width: 44, height: 44, borderRadius: 12, background: 'linear-gradient(135deg, #22d3ee, #22c55e)', display: 'grid', placeItems: 'center', color: '#06121a', fontWeight: 700, fontSize: '1.4rem' }}>✓</div>
                    <div>
                      <h3 style={{ color: '#86efac' }}>{t('premium_unlocked_title')}</h3>
                      <p style={{ color: 'var(--muted)', fontSize: '.85rem' }}>{t('premium_unlocked_desc')}</p>
                    </div>
                  </div>
                  <ul style={{ listStyle: 'none', padding: 0, margin: '8px 0 0', display: 'grid', gap: 6 }}>
                    {features.map((f) => (
                      <li key={f} style={{ display: 'flex', gap: 8, fontSize: '.9rem' }}>
                        <span style={{ color: 'var(--accent-2)' }}>✓</span> {f}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : (
                <>
                  <div className="map-wrap" style={{ height: 460, marginTop: 14 }}>
                    {!iframeLoaded && (
                      <div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', color: 'var(--muted)', zIndex: 5 }}>
                        Loading Chariow checkout…
                      </div>
                    )}
                    <iframe
                      title="Chariow checkout"
                      src={subscription.chariow_checkout_url}
                      onLoad={() => setIframeLoaded(true)}
                      style={{ width: '100%', height: '100%', border: 0, background: 'white' }}
                      allow="payment *; clipboard-write"
                    />
                  </div>

                  <div className="form-actions" style={{ alignItems: 'center' }}>
                    <a className="btn btn-ghost" href={subscription.chariow_checkout_url} target="_blank" rel="noreferrer">
                      {t('premium_open_external')} ↗
                    </a>
                    <button className="btn btn-primary" onClick={simulatePayment}>
                      {t('premium_simulate')}
                    </button>
                    <span className="kbd" style={{ alignSelf: 'center' }}>{t('premium_prototype_badge')}</span>
                  </div>
                  <p style={{ color: 'var(--muted)', fontSize: '.8rem', marginTop: 8 }}>{t('premium_simulate_hint')}</p>
                </>
              )}
            </>
          )}
        </div>
      </section>
    </div>
  )
}
