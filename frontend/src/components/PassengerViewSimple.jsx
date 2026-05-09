import { useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import { useI18n } from '../i18n/useI18n'
import DriverSMSView from './DriverSMSView'

// Composant chauffeur simplifié - juste l'essentiel
function DriverCardSimple({ driver, score, status, onSelect }) {
  const { t } = useI18n()
  
  const getColor = () => {
    if (score >= 80) return '#059669' // vert foncé naturel
    if (score >= 50) return '#d97706' // orange chaud
    return '#dc2626' // rouge profond
  }
  
  const getBgColor = () => {
    if (score >= 80) return '#d1fae5' // vert très clair
    if (score >= 50) return '#fef3c7' // jaune très clair
    return '#fee2e2' // rouge très clair
  }
  
  const getLabel = () => {
    if (score >= 80) return t('verified')
    if (score >= 50) return t('caution')
    return t('blocked')
  }
  
  const initials = driver.name.split(' ').map(n => n[0]).join('').slice(0, 2)
  
  return (
    <div style={{
      padding: '16px',
      background: '#ffffff',
      borderRadius: '12px',
      border: `2px solid ${getColor()}`,
      marginBottom: '12px',
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
    }}>
      {/* Avatar */}
      <div style={{
        width: '50px',
        height: '50px',
        borderRadius: '50%',
        background: driver.avatar_color,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '18px',
        fontWeight: 'bold',
        color: 'white'
      }}>
        {initials}
      </div>
      
      {/* Info */}
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: '600', fontSize: '16px', marginBottom: '4px', color: '#1f2937' }}>
          {driver.name}
        </div>
        <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>
          {driver.vehicle} • {driver.plate}
        </div>
        <div style={{ fontSize: '13px', color: '#6b7280' }}>
          ⭐ {driver.rating.toFixed(1)} • {driver.rides_completed} courses
        </div>
      </div>
      
      {/* Score */}
      <div style={{ textAlign: 'center' }}>
        <div style={{
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: `${getColor()}20`,
          border: `3px solid ${getColor()}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '20px',
          fontWeight: 'bold',
          color: getColor()
        }}>
          {Math.round(score)}
        </div>
        <div style={{ 
          fontSize: '11px', 
          color: getColor(), 
          marginTop: '4px',
          fontWeight: '600',
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          {getLabel()}
        </div>
      </div>
      
      {/* Boutons */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {status !== 'blocked' && (
          <button 
            onClick={onSelect}
            style={{
              padding: '10px 20px',
              background: '#22d3ee',
              color: '#0f172a',
              border: 'none',
              borderRadius: '8px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            {t('book')}
          </button>
        )}
      </div>
    </div>
  )
}

// Vue principale simplifiée
export default function PassengerViewSimple({ cities }) {
  const { t, lang } = useI18n()
  const [step, setStep] = useState(1) // 1: formulaire, 2: résultats, 3: course active
  
  const [city, setCity] = useState('Douala')
  const cityInfo = useMemo(() => cities.find((c) => c.code === city), [cities, city])
  const neighborhoods = cityInfo?.neighborhoods ?? []
  
  const [pickupCode, setPickupCode] = useState('')
  const [destCode, setDestCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [drivers, setDrivers] = useState([])
  const [selectedDriver, setSelectedDriver] = useState(null)
  const [rideStatus, setRideStatus] = useState(null)
  
  // SMS Simulation pour le hackathon
  const [showSMS, setShowSMS] = useState(false)
  const [smsRequest, setSmsRequest] = useState(null)
  
  // Initialiser les quartiers par défaut
  useEffect(() => {
    if (neighborhoods.length >= 2) {
      setPickupCode(neighborhoods[0].code)
      setDestCode(neighborhoods[1].code)
    }
  }, [neighborhoods])
  
  const searchDrivers = async () => {
    setLoading(true)
    try {
      const pickup = neighborhoods.find(n => n.code === pickupCode)
      const dest = neighborhoods.find(n => n.code === destCode)
      
      const data = await api.requestRide({
        passenger_name: 'Passager',
        city,
        pickup: { lat: pickup.coordinates.lat, lng: pickup.coordinates.lng },
        destination: { lat: dest.coordinates.lat, lng: dest.coordinates.lng },
        radius_km: 5,
      })
      
      // Combiner tous les chauffeurs en une seule liste
      const allDrivers = [
        ...data.reliable.map(d => ({ ...d, category: 'reliable' })),
        ...data.attention.map(d => ({ ...d, category: 'attention' })),
        ...data.blocked.map(d => ({ ...d, category: 'blocked' }))
      ]
      setDrivers(allDrivers)
      setStep(2)
    } catch (e) {
      alert('Erreur: ' + e.message)
    } finally {
      setLoading(false)
    }
  }
  
  const bookDriver = async (driverData) => {
    // Au lieu de confirmer directement, on montre la simulation SMS
    const pickup = neighborhoods.find(n => n.code === pickupCode)
    const dest = neighborhoods.find(n => n.code === destCode)
    
    // Préparer les données pour le SMS
    setSmsRequest({
      pickup: pickup?.label || pickupCode,
      destination: dest?.label || destCode,
      fare: driverData.fare_xaf,
      passenger: 'Jules N.',
      driverName: driverData.driver.name,
      driverPhone: driverData.driver.phone_number
    })
    
    setSelectedDriver(driverData)
    setShowSMS(true)
  }
  
  // Quand le chauffeur accepte par SMS
  const handleDriverAccept = async () => {
    setShowSMS(false)
    setLoading(true)
    
    try {
      const pickup = neighborhoods.find(n => n.code === pickupCode)
      const dest = neighborhoods.find(n => n.code === destCode)
      
      const ride = await api.startRide({
        passenger_name: 'Jules N.',
        city,
        pickup: { lat: pickup.coordinates.lat, lng: pickup.coordinates.lng },
        destination: { lat: dest.coordinates.lat, lng: dest.coordinates.lng },
        selected_driver_id: selectedDriver.driver.id,
        radius_km: 5,
      })
      
      setRideStatus(ride)
      setStep(3)
    } catch (e) {
      alert('Erreur: ' + e.message)
    } finally {
      setLoading(false)
    }
  }
  
  // Quand le chauffeur refuse ou ne répond pas
  const handleDriverReject = () => {
    setShowSMS(false)
    alert(lang === 'fr' 
      ? 'Le chauffeur a refusé ou n\'a pas répondu à temps. Choisissez un autre chauffeur.' 
      : 'Driver declined or did not respond in time. Please choose another driver.')
    // Reste sur la liste des chauffeurs
  }
  
  // ÉTAPE 1 : Formulaire simple
  const renderStep1 = () => {
    const fieldStyle = {
      width: '100%',
      height: '52px',
      padding: '0 16px',
      background: 'rgba(30,41,59,0.96)',
      border: '1px solid #475569',
      borderRadius: '12px',
      color: 'white',
      fontSize: '16px',
    }

    return (
      <main className="container" style={{ paddingTop: '28px', paddingBottom: '36px' }}>
        <div style={{
          maxWidth: '760px',
          margin: '0 auto 24px',
          textAlign: 'center',
          color: '#b8c7e6',
          fontSize: '18px',
          lineHeight: '1.6',
        }}>
          {t('hero_desc')}
        </div>

        <section style={{
          width: '100%',
          maxWidth: '620px',
          margin: '0 auto',
          padding: '28px',
          background: 'rgba(15,23,42,0.94)',
          border: '1px solid rgba(148,163,184,0.24)',
          borderRadius: '22px',
          boxShadow: '0 24px 70px rgba(0,0,0,0.35)',
        }}>
          <h1 style={{ fontSize: '28px', marginBottom: '8px' }}>{t('book_ride')}</h1>
          <p style={{ color: '#94a3b8', marginBottom: '24px' }}>{t('book_subtitle')}</p>

          <div style={{ display: 'grid', gap: '18px' }}>
            <label style={{ display: 'grid', gap: '8px', fontSize: '14px' }}>
              {t('city')}
              <select value={city} onChange={(e) => setCity(e.target.value)} style={fieldStyle}>
                {cities.map((c) => (<option key={c.code} value={c.code}>{c.label}</option>))}
              </select>
            </label>

            <label style={{ display: 'grid', gap: '8px', fontSize: '14px' }}>
              {t('departure')}
              <select value={pickupCode} onChange={(e) => setPickupCode(e.target.value)} style={fieldStyle}>
                {neighborhoods.map((n) => (<option key={n.code} value={n.code}>{n.label}</option>))}
              </select>
            </label>

            <label style={{ display: 'grid', gap: '8px', fontSize: '14px' }}>
              {t('arrival')}
              <select value={destCode} onChange={(e) => setDestCode(e.target.value)} style={fieldStyle}>
                {neighborhoods.map((n) => (<option key={n.code} value={n.code}>{n.label}</option>))}
              </select>
            </label>

            <button
              onClick={searchDrivers}
              disabled={loading}
              style={{
                width: '100%',
                height: '56px',
                marginTop: '6px',
                background: 'linear-gradient(135deg, #22d3ee, #22c55e)',
                color: '#0f172a',
                border: 'none',
                borderRadius: '12px',
                fontSize: '18px',
                fontWeight: 'bold',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.7 : 1,
              }}
            >
              {loading ? t('searching') : t('find_drivers')}
            </button>
          </div>
        </section>
      </main>
    )
  }
  
  // ÉTAPE 2 : Liste des chauffeurs
  const renderStep2 = () => (
    <div style={{ maxWidth: '700px', margin: '0 auto', padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h1 style={{ fontSize: '24px' }}>{t('available_drivers')}</h1>
          <button 
            onClick={() => setStep(1)}
            style={{
              padding: '8px 16px',
              background: 'transparent',
              border: '1px solid #475569',
              borderRadius: '6px',
              color: '#94a3b8',
              cursor: 'pointer'
            }}
          >
            {t('modify')}
          </button>
        </div>
        
        <div style={{ marginBottom: '20px', padding: '12px', background: 'rgba(30,41,59,0.5)', borderRadius: '8px' }}>
          <strong>{cityInfo?.label}</strong> • {t('from')} <strong>{neighborhoods.find(n => n.code === pickupCode)?.label}</strong> {t('to')} <strong>{neighborhoods.find(n => n.code === destCode)?.label}</strong>
        </div>
        
        {drivers.length === 0 ? (
          <p style={{ color: '#94a3b8' }}>{t('no_drivers')}</p>
        ) : (
          <>
            <p style={{ marginBottom: '16px', color: '#94a3b8' }}>
              {drivers.length} {t('drivers_found')}
            </p>
            {drivers.map((driverData) => (
              <DriverCardSimple
                key={driverData.driver.id}
                driver={driverData.driver}
                score={driverData.trust_score}
                status={driverData.status}
                onSelect={() => bookDriver(driverData)}
              />
            ))}
          </>
        )}
      </div>
  )
  
  // ÉTAPE 3 : Course en cours
  const renderStep3 = () => (
    (step === 3 && selectedDriver && rideStatus) ? (
      <div style={{ maxWidth: '500px', margin: '0 auto', padding: '20px' }}>
        <h1 style={{ fontSize: '24px', marginBottom: '8px' }}>🎉 {t('ride_booked')}</h1>
        
        <div style={{
          padding: '20px',
          background: 'rgba(34,197,94,0.1)',
          border: '2px solid #22c55e',
          borderRadius: '12px',
          marginBottom: '20px'
        }}>
          <h2 style={{ fontSize: '20px', marginBottom: '8px' }}>{selectedDriver.driver.name}</h2>
          <p style={{ color: '#94a3b8', marginBottom: '8px' }}>
            {selectedDriver.driver.vehicle} • {selectedDriver.driver.plate}
          </p>
          <p style={{ fontSize: '18px', fontWeight: 'bold', color: '#22c55e' }}>
            {t('estimated_fare')}: {selectedDriver.fare_xaf.toLocaleString()} FCFA
          </p>
        </div>
        
        <div style={{ 
          padding: '16px', 
          background: 'rgba(30,41,59,0.8)', 
          borderRadius: '10px',
          marginBottom: '20px'
        }}>
          <h3 style={{ marginBottom: '12px' }}>{t('what_happens_now')}</h3>
          <ol style={{ paddingLeft: '20px', lineHeight: '1.8', color: '#94a3b8' }}>
            <li>{t('step1_sms')}</li>
            <li>{t('step2_confirm')}</li>
            <li>{t('step3_arrive')}</li>
            <li>{t('step4_pay')}</li>
          </ol>
        </div>
        
        <div style={{
          padding: '16px',
          background: 'rgba(245,158,11,0.1)',
          border: '1px solid #f59e0b',
          borderRadius: '10px',
          marginBottom: '20px'
        }}>
          <strong style={{ color: '#f59e0b' }}>⚠️ {t('security_note_title')}</strong>
          <p style={{ marginTop: '8px', fontSize: '14px', color: '#94a3b8' }}>
            {t('security_note_text')}
          </p>
        </div>
        
        <button 
          onClick={() => {
            setStep(1)
            setSelectedDriver(null)
            setRideStatus(null)
            setDrivers([])
          }}
          style={{
            width: '100%',
            padding: '14px',
            background: '#475569',
            color: 'white',
            border: 'none',
            borderRadius: '10px',
            cursor: 'pointer'
          }}
        >
          {t('book_another')}
        </button>
    </div>
    ) : null
  )
  
  // Rendu du SMS si actif (par-dessus tout)
  return (
    <>
      {/* Contenu principal basé sur l'étape */}
      {step === 1 && renderStep1()}
      {step === 2 && renderStep2()}
      {step === 3 && renderStep3()}
      
      {/* SMS Simulation Modal */}
      {showSMS && (
        <DriverSMSView
          rideRequest={smsRequest}
          onAccept={handleDriverAccept}
          onReject={handleDriverReject}
          onClose={handleDriverReject}
        />
      )}
    </>
  )
}
