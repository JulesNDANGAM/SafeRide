import { useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import { useI18n } from '../i18n/useI18n'
import DriverCard from './DriverCard'

export default function OpsView({ cities }) {
  const { t } = useI18n()
  const [city, setCity] = useState('Douala')
  const [snapshots, setSnapshots] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    api.drivers(city).then(setSnapshots).catch((e) => setError(e.message))
  }, [city])

  const stats = useMemo(() => {
    if (!snapshots.length) return { total: 0, avg: 0, blocked: 0, fraud: 0 }
    const total = snapshots.length
    const avg = Math.round(snapshots.reduce((s, x) => s + x.trust_score, 0) / total)
    const blocked = snapshots.filter((s) => s.status === 'blocked').length
    const fraud = snapshots.reduce((s, x) => s + x.anomalies.length, 0)
    return { total, avg, blocked, fraud }
  }, [snapshots])

  return (
    <div className="container section">
      <section className="card">
        <div className="form-grid" style={{ gridTemplateColumns: '1fr auto' }}>
          <div>
            <h2>{t('ops_title')}</h2>
            <p style={{ color: 'var(--muted)', marginTop: 6 }}>{t('ops_desc')}</p>
          </div>
          <label>
            <span>{t('city')}</span>
            <select value={city} onChange={(e) => setCity(e.target.value)}>
              {cities.map((c) => (<option key={c.code} value={c.code}>{c.label}</option>))}
            </select>
          </label>
        </div>

        {error && <div className="error-banner">{error}</div>}

        <div className="stats" style={{ marginTop: 18 }}>
          <div className="stat"><strong>{stats.total}</strong><span>{t('total_drivers')}</span></div>
          <div className="stat"><strong>{stats.avg}</strong><span>{t('avg_score')}</span></div>
          <div className="stat"><strong>{stats.blocked}</strong><span>{t('blocked_count')}</span></div>
          <div className="stat"><strong>{stats.fraud}</strong><span>{t('fraud_signals')}</span></div>
        </div>
      </section>

      <section className="section">
        <div className="bucket-grid">
          <div className="bucket">
            <h3><span className="bucket-dot good" /> {t('reliable')}</h3>
            <div className="driver-list">
              {snapshots.filter((s) => s.status === 'reliable').map((s) => (<DriverCard key={s.driver.id} snap={s} defaultDetailsOpen />))}
            </div>
          </div>
          <div className="bucket">
            <h3><span className="bucket-dot warn" /> {t('attention')}</h3>
            <div className="driver-list">
              {snapshots.filter((s) => s.status === 'attention').map((s) => (<DriverCard key={s.driver.id} snap={s} defaultDetailsOpen />))}
            </div>
          </div>
          <div className="bucket">
            <h3><span className="bucket-dot bad" /> {t('blocked')}</h3>
            <div className="driver-list">
              {snapshots.filter((s) => s.status === 'blocked').map((s) => (<DriverCard key={s.driver.id} snap={s} defaultDetailsOpen />))}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
