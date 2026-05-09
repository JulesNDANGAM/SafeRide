import { useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import { useI18n } from '../i18n/useI18n'

function scoreClass(score) {
  if (score >= 70) return 'score-good'
  if (score >= 40) return 'score-warn'
  return 'score-bad'
}

export default function DriverView({ cities }) {
  const { t } = useI18n()
  const [city, setCity] = useState('Douala')
  const [snapshots, setSnapshots] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.drivers(city).then((data) => {
      setSnapshots(data)
      setSelectedId(data[0]?.driver.id ?? null)
    }).catch((e) => setError(e.message))
  }, [city])

  const snap = useMemo(() => snapshots.find((s) => s.driver.id === selectedId), [snapshots, selectedId])
  return (
    <div className="container section">
      <section className="grid-2">
        <div className="card">
          <h2>{t('driver_dashboard')}</h2>
          <div className="form-grid">
            <label>
              <span>{t('city')}</span>
              <select value={city} onChange={(e) => setCity(e.target.value)}>
                {cities.map((c) => (<option key={c.code} value={c.code}>{c.label}</option>))}
              </select>
            </label>
            <label>
              <span>{t('driver_select')}</span>
              <select value={selectedId ?? ''} onChange={(e) => setSelectedId(e.target.value)}>
                {snapshots.map((s) => (<option key={s.driver.id} value={s.driver.id}>{s.driver.name}</option>))}
              </select>
            </label>
          </div>
          {error && <div className="error-banner">{error}</div>}
        </div>

        {snap && (
          <div className="card">
            <div className="driver-card-head">
              <div className="avatar" style={{ background: snap.driver.avatar_color }}>
                {snap.driver.name.split(' ').map((p) => p[0]).slice(0,2).join('')}
              </div>
              <div className="driver-meta">
                <div className="driver-name">{snap.driver.name}</div>
                <div className="driver-sub">
                  {t('operator')}: {snap.driver.carrier} · ★ {snap.driver.rating.toFixed(1)} · {snap.driver.rides_completed} {t('rides_completed')}
                </div>
              </div>
              <div className={`driver-score ${scoreClass(snap.trust_score)}`}>{snap.trust_score}</div>
            </div>
            <div className="driver-info-mini" style={{ marginTop: 12 }}>
              <span>{t('vehicle')}: {snap.driver.vehicle}</span>
              <span>{t('plate')}: {snap.driver.plate}</span>
              <span>{snap.qod_active ? t('qod_active') : t('qod_inactive')}</span>
              <span>{snap.driver.inside_geofence ? t('inside_geofence') : t('outside_geofence')}</span>
            </div>
          </div>
        )}
      </section>

    </div>
  )
}
