import { useState } from 'react'
import { api } from '../api'
import { useI18n } from '../i18n/useI18n'

function scoreClass(score) {
  if (score >= 70) return 'score-good'
  if (score >= 40) return 'score-warn'
  return 'score-bad'
}

function barClass(score) {
  if (score >= 70) return ''
  if (score >= 40) return 'warn'
  return 'bad'
}

export default function DriverCard({ snap, onSelect, defaultDetailsOpen = false }) {
  const { t, lang } = useI18n()
  const [insight, setInsight] = useState(snap.llm_insight ?? null)
  const [explaining, setExplaining] = useState(false)
  const [aiError, setAiError] = useState('')
  const [showDetails, setShowDetails] = useState(defaultDetailsOpen)
  const initials = snap.driver.name.split(' ').map((p) => p[0]).slice(0, 2).join('')
  const bd = snap.breakdown
  const isReliable = snap.status === 'reliable'
  const checks = [bd.sim_swap, bd.location_verification, bd.device_status, bd.number_verification]
  const checksPassed = checks.filter((v) => v >= 70).length

  async function explain() {
    setExplaining(true); setAiError('')
    try {
      const enriched = await api.explainDriver(snap.driver.id, snap.driver.city)
      setInsight(enriched.llm_insight)
    } catch (e) { setAiError(e.message) }
    finally { setExplaining(false) }
  }

  function recClass(rec) {
    if (rec === 'accept') return 'score-good'
    if (rec === 'reject') return 'score-bad'
    return 'score-warn'
  }

  return (
    <article className="driver-card">
      <div className="driver-card-head">
        <div className="avatar" style={{ background: snap.driver.avatar_color }}>{initials}</div>
        <div className="driver-meta">
          <div className="driver-name">{snap.driver.name}</div>
          <div className="driver-sub">
            {snap.driver.vehicle} · {snap.driver.plate} · {snap.driver.carrier}
          </div>
        </div>
        <div className={`driver-score ${scoreClass(snap.trust_score)}`}>{snap.trust_score}</div>
      </div>

      <div className="driver-info-mini">
        <span>★ {snap.driver.rating.toFixed(1)} · {snap.driver.rides_completed} {t('rides_completed')}</span>
        <span>{t('eta')}: {snap.eta_minutes} min · {snap.distance_km} km</span>
        <span>{t('fare')}: {snap.fare_xaf.toLocaleString()} XAF</span>
        <span>{t('checks_passed')}: {checksPassed} / 4</span>
      </div>

      {showDetails && (
        <>
          <div className="bars">
            {[
              ['sim_swap', bd.sim_swap],
              ['location_verification', bd.location_verification],
              ['device_status', bd.device_status],
              ['number_verification', bd.number_verification],
            ].map(([key, val]) => (
              <div className="bar" key={key}>
                <span>{t(key)}</span>
                <div className="bar-track">
                  <div className={`bar-fill ${barClass(val)}`} style={{ width: `${val}%` }} />
                </div>
                <div className="bar-val">{val}</div>
              </div>
            ))}
          </div>

          {(snap.anomalies.length > 0 || snap.monitoring_alerts.length > 0) && (
            <div className="flag-list">
              {snap.anomalies.map((a, i) => (<div className="flag" key={`a${i}`}>{a}</div>))}
              {snap.monitoring_alerts.map((a, i) => (<div className="flag warn" key={`m${i}`}>{a}</div>))}
            </div>
          )}
        </>
      )}

      {insight && (
        <div
          className="card tight"
          style={{
            marginTop: 10,
            background: 'rgba(34,211,238,.06)',
            borderColor: 'rgba(34,211,238,.3)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
            <span style={{ color: 'var(--accent)', fontSize: '.78rem', fontWeight: 700, letterSpacing: '.04em' }}>
              {t('ai_recommendation')}
            </span>
            <span className={`sig-score ${recClass(insight.recommendation)}`} style={{ fontSize: '.78rem', padding: '4px 8px' }}>
              {t(`ai_rec_${insight.recommendation}`) || insight.recommendation}
            </span>
          </div>
          <p style={{ fontSize: '.85rem', margin: 0 }}>
            {lang === 'fr' ? insight.message_fr : insight.message_en}
          </p>
          <div style={{ marginTop: 6, color: 'var(--muted)', fontSize: '.7rem' }}>
            {t('ai_powered_by')} <code>{insight.model}</code>
            {!insight.used_llm && <> · {t('ai_fallback_note')}</>}
          </div>
        </div>
      )}
      {aiError && <div className="error-banner" style={{ fontSize: '.8rem' }}>{aiError}</div>}

      <div className="driver-action">
        <button className="btn btn-ghost" onClick={() => setShowDetails((v) => !v)}>
          {showDetails ? t('hide_details') : t('show_details')}
        </button>
        <button className="btn btn-ghost" onClick={explain} disabled={explaining}>
          {explaining ? t('ai_thinking') : t('ai_explain')}
        </button>
        {onSelect && (
          <button
            className="btn btn-primary"
            disabled={!isReliable}
            onClick={() => onSelect(snap.driver.id)}
          >
            {isReliable ? t('select_driver') : t('cannot_select')}
          </button>
        )}
      </div>
    </article>
  )
}
