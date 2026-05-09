import { useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import { useI18n } from '../i18n/useI18n'
import MapView from './MapView'
import DriverCard from './DriverCard'

export default function PassengerView({ cities }) {
  const { t, lang } = useI18n()

  const [city, setCity] = useState('Douala')
  const cityInfo = useMemo(() => cities.find((c) => c.code === city), [cities, city])
  const neighborhoods = cityInfo?.neighborhoods ?? []
  const [pickupCode, setPickupCode] = useState('')
  const [destCode, setDestCode] = useState('')
  const [pickup, setPickup] = useState(null)
  const [destination, setDestination] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [board, setBoard] = useState({ reliable: [], attention: [], blocked: [] })
  const [activeRide, setActiveRide] = useState(null)

  // When the city changes, seed pickup = first neighborhood, destination = second
  useEffect(() => {
    if (!cityInfo) return
    const list = cityInfo.neighborhoods ?? []
    if (list.length >= 2) {
      setPickupCode(list[0].code)
      setDestCode(list[1].code)
    } else if (list.length === 1) {
      setPickupCode(list[0].code)
      setDestCode(list[0].code)
    } else {
      setPickupCode('')
      setDestCode('')
    }
  }, [cityInfo])

  // Resolve neighborhood code -> coordinates
  useEffect(() => {
    const p = neighborhoods.find((n) => n.code === pickupCode)
    const d = neighborhoods.find((n) => n.code === destCode)
    setPickup(p ? [p.coordinates.lat, p.coordinates.lng] : null)
    setDestination(d ? [d.coordinates.lat, d.coordinates.lng] : null)
  }, [pickupCode, destCode, neighborhoods])

  // Auto-evaluate when both pickup and destination are set
  useEffect(() => {
    if (!pickup || !destination) return
    evaluate()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pickupCode, destCode, city])

  async function evaluate() {
    if (!pickup || !destination) {
      setError(t('select_pickup_first'))
      return
    }
    setLoading(true); setError('')
    try {
      const data = await api.requestRide({
        passenger_name: 'Passager',
        city,
        pickup: { lat: pickup[0], lng: pickup[1] },
        destination: { lat: destination[0], lng: destination[1] },
        radius_km: 5,
      })
      setBoard({ reliable: data.reliable, attention: data.attention, blocked: data.blocked })
      setActiveRide(null)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  async function startRide(driverId) {
    setLoading(true); setError('')
    try {
      const ride = await api.startRide({
        passenger_name: 'Passager',
        city,
        pickup: { lat: pickup[0], lng: pickup[1] },
        destination: { lat: destination[0], lng: destination[1] },
        selected_driver_id: driverId,
        radius_km: 5,
      })
      setActiveRide(ride)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  async function monitor(kind) {
    if (!activeRide) return
    const payload = {
      simulate_route_deviation: kind === 'route',
      simulate_network_drop: kind === 'network',
      simulate_location_mismatch: kind === 'location',
      simulate_congestion_spike: kind === 'congestion',
    }
    try {
      const updated = await api.monitor(activeRide.id, payload)
      setActiveRide(updated)
    } catch (e) { setError(e.message) }
  }

  async function complete() {
    if (!activeRide) return
    try {
      const updated = await api.complete(activeRide.id)
      setActiveRide(updated)
    } catch (e) { setError(e.message) }
  }

  const allSnapshots = [...board.reliable, ...board.attention, ...board.blocked]
  const center = cityInfo ? [cityInfo.center.lat, cityInfo.center.lng] : [4.05, 9.76]
  const totalAround = allSnapshots.length

  return (
    <div className="container section">
      <section className="grid-2">
        <div className="card">
          <h2>{t('cta_request')}</h2>
          <p style={{ color: 'var(--muted)', fontSize: '.88rem', margin: '4px 0 14px' }}>
            {t('passenger_help')}
          </p>
          <div className="form-grid">
            <label>
              <span>{t('city')}</span>
              <select value={city} onChange={(e) => setCity(e.target.value)}>
                {cities.map((c) => (<option key={c.code} value={c.code}>{c.label}, {c.country}</option>))}
              </select>
            </label>
            <label>
              <span>{t('pickup')}</span>
              <select value={pickupCode} onChange={(e) => setPickupCode(e.target.value)}>
                <option value="">{t('select_neighborhood')}</option>
                {neighborhoods.map((n) => (<option key={n.code} value={n.code}>{n.label}</option>))}
              </select>
            </label>
            <label>
              <span>{t('destination')}</span>
              <select value={destCode} onChange={(e) => setDestCode(e.target.value)}>
                <option value="">{t('select_neighborhood')}</option>
                {neighborhoods.map((n) => (<option key={n.code} value={n.code}>{n.label}</option>))}
              </select>
            </label>
          </div>

          <div className="form-actions">
            <button className="btn btn-primary" onClick={evaluate} disabled={loading}>
              {loading ? t('request_loading') : t('cta_request')}
            </button>
          </div>

          {error && <div className="error-banner">{error}</div>}
          <div style={{ marginTop: 14, padding: '10px 12px', borderRadius: 10, background: 'rgba(255,255,255,.04)', border: '1px solid rgba(255,255,255,.08)', fontSize: '.78rem', color: 'var(--muted)' }}>
            {t('demo_data_notice')}
          </div>
        </div>

        <div className="map-wrap">
          <div className="map-overlay">
            <span className="map-pill">{cityInfo?.label} · {cityInfo?.country}</span>
            <span className="map-pill">{totalAround} {t('drivers_around')}</span>
            {cityInfo?.operator_partner && (
              <span className="map-pill">{cityInfo.operator_partner}</span>
            )}
          </div>
          <MapView
            center={center}
            pickup={pickup}
            destination={destination}
            snapshots={allSnapshots}
            onSetPickup={setPickup}
            onSetDestination={setDestination}
          />
        </div>
      </section>

      <section className="section">
        <div className="bucket-grid">
          <div className="bucket">
            <h3><span className="bucket-dot good" /> {t('reliable')} ({board.reliable.length})</h3>
            {board.reliable.length === 0 && <div className="bucket-empty">{t('bucket_empty')}</div>}
            <div className="driver-list">
              {board.reliable.map((s) => (<DriverCard key={s.driver.id} snap={s} onSelect={startRide} />))}
            </div>
          </div>
          <div className="bucket">
            <h3><span className="bucket-dot warn" /> {t('attention')} ({board.attention.length})</h3>
            {board.attention.length === 0 && <div className="bucket-empty">{t('bucket_empty')}</div>}
            <div className="driver-list">
              {board.attention.map((s) => (<DriverCard key={s.driver.id} snap={s} onSelect={startRide} />))}
            </div>
          </div>
          <div className="bucket">
            <h3><span className="bucket-dot bad" /> {t('blocked')} ({board.blocked.length})</h3>
            {board.blocked.length === 0 && <div className="bucket-empty">{t('bucket_empty')}</div>}
            <div className="driver-list">
              {board.blocked.map((s) => (<DriverCard key={s.driver.id} snap={s} />))}
            </div>
          </div>
        </div>
      </section>

      <section className="card">
        <h2>{t('monitoring')}</h2>
        {!activeRide ? (
          <p style={{ color: 'var(--muted)' }}>{t('no_active_ride')}</p>
        ) : (
          <div className="grid-2">
            <div>
              <div className="driver-card-head" style={{ marginBottom: 12 }}>
                <div className="avatar" style={{ background: activeRide.trust_snapshot.driver.avatar_color }}>
                  {activeRide.trust_snapshot.driver.name.split(' ').map((p) => p[0]).slice(0,2).join('')}
                </div>
                <div className="driver-meta">
                  <div className="driver-name">{activeRide.trust_snapshot.driver.name}</div>
                  <div className="driver-sub">
                    {activeRide.trust_snapshot.driver.vehicle} · {activeRide.trust_snapshot.driver.plate}
                  </div>
                </div>
                <div className={`driver-score ${activeRide.trust_snapshot.trust_score >= 70 ? 'score-good' : 'score-warn'}`}>
                  {activeRide.trust_snapshot.trust_score}
                </div>
              </div>

              <div className="driver-info-mini" style={{ marginBottom: 12 }}>
                <span>{t('cycle')}: {activeRide.monitoring_cycle}</span>
                <span>{t('fare')}: {activeRide.fare_xaf.toLocaleString()} XAF</span>
                <span>Status: {activeRide.status}</span>
              </div>

              <div className="form-actions">
                <button className="btn btn-ghost" onClick={() => monitor('heartbeat')}>{t('heartbeat')}</button>
                <button className="btn btn-ghost" onClick={() => monitor('route')}>{t('sim_route')}</button>
                <button className="btn btn-ghost" onClick={() => monitor('network')}>{t('sim_network')}</button>
                <button className="btn btn-ghost" onClick={() => monitor('location')}>{t('sim_location')}</button>
                <button className="btn btn-ghost" onClick={() => monitor('congestion')}>{t('sim_congestion')}</button>
                <button className="btn btn-primary" onClick={complete}>{t('complete_ride')}</button>
              </div>
            </div>

            <div>
              <h3 style={{ marginBottom: 8 }}>{t('events')}</h3>
              <div className="timeline">
                {[...activeRide.events].reverse().map((ev, i) => (
                  <div className={`event ${ev.severity}`} key={i}>
                    <div className="ev-head">
                      <span>#{ev.cycle} · {ev.code}</span>
                      <span>{ev.timestamp_iso.replace('T', ' ').replace('Z', '')}</span>
                    </div>
                    <div>{lang === 'fr' ? ev.message_fr : ev.message_en}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </section>
    </div>
  )
}
