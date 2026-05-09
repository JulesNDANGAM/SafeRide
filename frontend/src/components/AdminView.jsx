import { useEffect, useState } from 'react'
import { api } from '../api'
import { useI18n } from '../i18n/useI18n'

const STORAGE_KEY = 'saferide.admin.token'

const EMPTY_DRIVER = {
  name: '', phone_number: '', carrier: '', city: 'Douala',
  vehicle: '', plate: '', rating: 4.5, rides_completed: 0,
  avatar_color: '#22d3ee',
  current_lat: 4.0511, current_lng: 9.7679,
  network_lat: 4.0511, network_lng: 9.7679,
  device_status: 'healthy', number_verified: true, sim_swap_recent: false,
  quality_on_demand_ready: true, congestion_level: 'low', inside_geofence: true,
}

function LoginCard({ onLogin }) {
  const { t } = useI18n()
  const [token, setToken] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setLoading(true); setError('')
    try {
      await api.admin.login(token)
      window.localStorage.setItem(STORAGE_KEY, token)
      onLogin(token)
    } catch (err) { setError(t('admin_invalid')) }
    finally { setLoading(false) }
  }

  return (
    <div className="container section">
      <form className="card" onSubmit={submit} style={{ maxWidth: 480, margin: '40px auto' }}>
        <h2>{t('admin_login_title')}</h2>
        <p style={{ color: 'var(--muted)', margin: '8px 0 16px' }}>{t('admin_login_desc')}</p>
        <label>
          <span style={{ display: 'block', marginBottom: 6, color: 'var(--muted)' }}>{t('admin_token')}</span>
          <input type="password" value={token} onChange={(e) => setToken(e.target.value)} placeholder="saferide-admin-dev" autoFocus />
        </label>
        <div className="form-actions">
          <button className="btn btn-primary" type="submit" disabled={loading || !token}>
            {loading ? '...' : t('admin_login_btn')}
          </button>
        </div>
        {error && <div className="error-banner">{error}</div>}
      </form>
    </div>
  )
}

function StatBlock({ label, value }) {
  return (<div className="stat"><strong>{value}</strong><span>{label}</span></div>)
}

function DriverForm({ initial, cities, onSave, onCancel }) {
  const { t } = useI18n()
  const [form, setForm] = useState(initial ?? EMPTY_DRIVER)
  const set = (k) => (e) => {
    const v = e.target.type === 'checkbox' ? e.target.checked
      : (e.target.type === 'number' ? Number(e.target.value) : e.target.value)
    setForm((f) => ({ ...f, [k]: v }))
  }
  return (
    <div className="card" style={{ marginTop: 16 }}>
      <div className="form-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
        <label><span>Name</span><input value={form.name} onChange={set('name')} /></label>
        <label><span>Phone</span><input value={form.phone_number} onChange={set('phone_number')} /></label>
        <label><span>Carrier</span><input value={form.carrier} onChange={set('carrier')} /></label>
        <label><span>City</span>
          <select value={form.city} onChange={set('city')}>
            {cities.map((c) => (<option key={c.code} value={c.code}>{c.label}</option>))}
          </select>
        </label>
        <label><span>Vehicle</span><input value={form.vehicle} onChange={set('vehicle')} /></label>
        <label><span>Plate</span><input value={form.plate} onChange={set('plate')} /></label>
        <label><span>Rating</span><input type="number" step="0.1" value={form.rating} onChange={set('rating')} /></label>
        <label><span>Rides completed</span><input type="number" value={form.rides_completed} onChange={set('rides_completed')} /></label>
        <label><span>Avatar color</span><input value={form.avatar_color} onChange={set('avatar_color')} /></label>
        <label><span>GPS lat</span><input type="number" step="0.0001" value={form.current_lat} onChange={set('current_lat')} /></label>
        <label><span>GPS lng</span><input type="number" step="0.0001" value={form.current_lng} onChange={set('current_lng')} /></label>
        <label><span>Network lat</span><input type="number" step="0.0001" value={form.network_lat} onChange={set('network_lat')} /></label>
        <label><span>Network lng</span><input type="number" step="0.0001" value={form.network_lng} onChange={set('network_lng')} /></label>
        <label><span>Device status</span>
          <select value={form.device_status} onChange={set('device_status')}>
            <option value="healthy">healthy</option>
            <option value="unknown">unknown</option>
            <option value="suspicious">suspicious</option>
          </select>
        </label>
        <label><span>Congestion</span>
          <select value={form.congestion_level} onChange={set('congestion_level')}>
            <option value="low">low</option>
            <option value="moderate">moderate</option>
            <option value="high">high</option>
          </select>
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input type="checkbox" checked={form.number_verified} onChange={set('number_verified')} style={{ width: 18 }} /> Number verified
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input type="checkbox" checked={form.sim_swap_recent} onChange={set('sim_swap_recent')} style={{ width: 18 }} /> SIM swap recent
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input type="checkbox" checked={form.quality_on_demand_ready} onChange={set('quality_on_demand_ready')} style={{ width: 18 }} /> QoD ready
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input type="checkbox" checked={form.inside_geofence} onChange={set('inside_geofence')} style={{ width: 18 }} /> Inside geofence
        </label>
      </div>
      <div className="form-actions">
        <button className="btn btn-primary" onClick={() => onSave(form)}>{t('admin_save')}</button>
        <button className="btn btn-ghost" onClick={onCancel}>{t('admin_cancel')}</button>
      </div>
    </div>
  )
}

function scoreClass(score) {
  if (score >= 70) return 'score-good'
  if (score >= 40) return 'score-warn'
  return 'score-bad'
}

export default function AdminView({ cities }) {
  const { t } = useI18n()
  const [token, setToken] = useState(() => window.localStorage.getItem(STORAGE_KEY) || '')
  const [authenticated, setAuthenticated] = useState(false)
  const [tab, setTab] = useState('drivers')
  const [stats, setStats] = useState(null)
  const [drivers, setDrivers] = useState([])
  const [rides, setRides] = useState([])
  const [subs, setSubs] = useState([])
  const [editingDriver, setEditingDriver] = useState(null)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) return
    api.admin.login(token).then(() => setAuthenticated(true)).catch(() => {
      window.localStorage.removeItem(STORAGE_KEY); setAuthenticated(false)
    })
  }, [token])

  async function refresh() {
    try {
      const [s, d, r, sb] = await Promise.all([
        api.admin.stats(token), api.admin.drivers(token),
        api.admin.rides(token), api.admin.subscriptions(token),
      ])
      setStats(s); setDrivers(d); setRides(r); setSubs(sb)
    } catch (e) { setError(e.message) }
  }

  useEffect(() => { if (authenticated) refresh() }, [authenticated]) // eslint-disable-line

  function logout() {
    window.localStorage.removeItem(STORAGE_KEY)
    setToken(''); setAuthenticated(false)
  }

  async function saveDriver(payload) {
    try {
      if (editingDriver) await api.admin.updateDriver(token, editingDriver.driver.id, payload)
      else await api.admin.createDriver(token, payload)
      setEditingDriver(null); setCreating(false)
      refresh()
    } catch (e) { setError(e.message) }
  }
  async function deleteDriver(id) {
    if (!window.confirm(t('admin_confirm_delete'))) return
    try { await api.admin.deleteDriver(token, id); refresh() }
    catch (e) { setError(e.message) }
  }
  async function cancelSub(id) {
    try { await api.admin.cancelSubscription(token, id); refresh() }
    catch (e) { setError(e.message) }
  }

  if (!authenticated) {
    return <LoginCard onLogin={(tk) => { setToken(tk); setAuthenticated(true) }} />
  }

  return (
    <div className="container section">
      <section className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h2>{t('admin_dashboard')}</h2>
            <p style={{ color: 'var(--muted)', marginTop: 6 }}>SafeRide control plane</p>
          </div>
          <button className="btn btn-ghost" onClick={logout}>{t('admin_logout')}</button>
        </div>

        {stats && (
          <div className="stats" style={{ marginTop: 18, gridTemplateColumns: 'repeat(6, 1fr)' }}>
            <StatBlock label={t('admin_kpi_drivers')} value={stats.total_drivers} />
            <StatBlock label={t('admin_kpi_avg')} value={stats.average_trust_score} />
            <StatBlock label={t('admin_kpi_blocked')} value={stats.blocked} />
            <StatBlock label={t('admin_kpi_rides')} value={stats.total_rides} />
            <StatBlock label={t('admin_kpi_subs')} value={stats.active_subscriptions} />
            <StatBlock label={t('admin_kpi_mrr')} value={stats.monthly_recurring_revenue_xaf.toLocaleString()} />
          </div>
        )}

        <div className="nav" style={{ marginTop: 18, width: 'fit-content' }}>
          {['drivers', 'rides', 'subs'].map((k) => (
            <button key={k} className={tab === k ? 'active' : ''} onClick={() => setTab(k)}>
              {t(`admin_tab_${k === 'subs' ? 'subs' : k}`)}
            </button>
          ))}
        </div>

        {error && <div className="error-banner">{error}</div>}
      </section>

      {tab === 'drivers' && (
        <section className="section">
          <div className="form-actions" style={{ marginBottom: 14 }}>
            <button className="btn btn-primary" onClick={() => { setCreating(true); setEditingDriver(null) }}>+ {t('admin_add_driver')}</button>
          </div>
          {(creating || editingDriver) && (
            <DriverForm
              initial={editingDriver ? {
                ...editingDriver.driver,
                current_lat: editingDriver.driver.current_location.lat,
                current_lng: editingDriver.driver.current_location.lng,
                network_lat: editingDriver.driver.network_location.lat,
                network_lng: editingDriver.driver.network_location.lng,
              } : null}
              cities={cities}
              onSave={saveDriver}
              onCancel={() => { setCreating(false); setEditingDriver(null) }}
            />
          )}
          <div className="card" style={{ marginTop: 16 }}>
            {drivers.length === 0 && <p style={{ color: 'var(--muted)' }}>{t('admin_no_data')}</p>}
            <div style={{ display: 'grid', gap: 8 }}>
              {drivers.map((s) => (
                <div className="signal-row" key={s.driver.id}>
                  <div>
                    <div className="sig-name">{s.driver.name} <span className="kbd">{s.driver.id}</span></div>
                    <div className="sig-cat">{s.driver.city} · {s.driver.carrier} · {s.driver.vehicle} · {s.driver.plate}</div>
                  </div>
                  <div className={`sig-score ${scoreClass(s.trust_score)}`}>{s.trust_score}</div>
                  <div style={{ display: 'flex', gap: 6 }}>
                    <button className="btn btn-ghost" onClick={() => { setEditingDriver(s); setCreating(false) }}>{t('admin_edit')}</button>
                    <button className="btn btn-ghost" onClick={() => deleteDriver(s.driver.id)}>{t('admin_delete')}</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {tab === 'rides' && (
        <section className="card section">
          {rides.length === 0 && <p style={{ color: 'var(--muted)' }}>{t('admin_no_data')}</p>}
          <div style={{ display: 'grid', gap: 8 }}>
            {rides.map((r) => (
              <div className="signal-row" key={r.id}>
                <div>
                  <div className="sig-name">{r.id} · {r.passenger_name}</div>
                  <div className="sig-cat">{r.city} · {r.trust_snapshot.driver.name} · cycle {r.monitoring_cycle}</div>
                </div>
                <div className="kbd">{r.fare_xaf.toLocaleString()} XAF</div>
                <div className={`sig-score ${r.status === 'completed' ? 'score-good' : 'score-warn'}`}>{r.status}</div>
              </div>
            ))}
          </div>
        </section>
      )}

      {tab === 'subs' && (
        <section className="card section">
          {subs.length === 0 && <p style={{ color: 'var(--muted)' }}>{t('admin_no_data')}</p>}
          <div style={{ display: 'grid', gap: 8 }}>
            {subs.map((s) => (
              <div className="signal-row" key={s.id}>
                <div>
                  <div className="sig-name">{s.id} · {s.driver_id}</div>
                  <div className="sig-cat">{s.created_at} · {s.last_chariow_event ?? '-'}</div>
                </div>
                <div className="kbd">{s.price_xaf.toLocaleString()} XAF</div>
                <div className={`sig-score ${s.status === 'active' ? 'score-good' : s.status === 'pending' ? 'score-warn' : 'score-bad'}`}>
                  {s.status}
                </div>
                {s.status !== 'cancelled' && (
                  <button className="btn btn-ghost" onClick={() => cancelSub(s.id)}>{t('admin_cancel_sub')}</button>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
