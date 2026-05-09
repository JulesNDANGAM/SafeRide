import { useI18n } from '../i18n/useI18n'

export default function AboutView() {
  const { t } = useI18n()

  const pillars = [
    { title: t('pillar_safety'), desc: t('pillar_safety_d'), icon: 'S' },
    { title: t('pillar_fraud'), desc: t('pillar_fraud_d'), icon: 'F' },
    { title: t('pillar_continuity'), desc: t('pillar_continuity_d'), icon: 'C' },
    { title: t('pillar_geo'), desc: t('pillar_geo_d'), icon: 'G' },
  ]

  return (
    <div className="container section">
      <section className="card">
        <h2>{t('concept_title')}</h2>
        <p style={{ color: 'var(--muted)', marginTop: 12 }}>{t('concept_p1')}</p>
        <p style={{ color: 'var(--muted)', marginTop: 12 }}>{t('concept_p2')}</p>

        <div className="pillars" style={{ marginTop: 22 }}>
          {pillars.map((p) => (
            <div className="pillar" key={p.title}>
              <div className="pi">{p.icon}</div>
              <h3>{p.title}</h3>
              <p>{p.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="card section">
        <h2>{t('rule_engine')}</h2>
        <div style={{ display: 'grid', gap: 10, marginTop: 12 }}>
          <div className="signal-row">
            <div><span className="bucket-dot good" /> &nbsp; {t('rule_70')}</div>
            <div className="kbd">70 → 100</div>
            <div className="sig-score score-good">OK</div>
          </div>
          <div className="signal-row">
            <div><span className="bucket-dot warn" /> &nbsp; {t('rule_40')}</div>
            <div className="kbd">40 → 69</div>
            <div className="sig-score score-warn">!</div>
          </div>
          <div className="signal-row">
            <div><span className="bucket-dot bad" /> &nbsp; {t('rule_0')}</div>
            <div className="kbd">0 → 39</div>
            <div className="sig-score score-bad">X</div>
          </div>
        </div>
        <p style={{ marginTop: 14, color: 'var(--muted)' }}>{t('proprietary_scoring_note')}</p>
      </section>
    </div>
  )
}
