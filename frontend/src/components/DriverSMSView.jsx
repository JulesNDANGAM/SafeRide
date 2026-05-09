import { useEffect, useState } from 'react'
import { useI18n } from '../i18n/useI18n'

// Simulation d'un téléphone basique qui reçoit des SMS
// Pour la démo hackathon - remplace l'application mobile
export default function DriverSMSView({ rideRequest, onAccept, onReject, onClose }) {
  const { t, lang } = useI18n()
  const [timeLeft, setTimeLeft] = useState(120) // 2 minutes pour répondre
  const [status, setStatus] = useState('received') // received, accepted, rejected, timeout
  const [showPhone, setShowPhone] = useState(true)

  useEffect(() => {
    if (status === 'received' && timeLeft > 0) {
      const timer = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            setStatus('timeout')
            return 0
          }
          return prev - 1
        })
      }, 1000)
      return () => clearInterval(timer)
    }
  }, [status, timeLeft])

  const handleAccept = () => {
    setStatus('accepted')
    onAccept?.()
  }

  const handleReject = () => {
    setStatus('rejected')
    onReject?.()
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (!rideRequest && status === 'received') return null

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px'
    }}>
      {/* Téléphone feature phone style */}
      <div style={{
        width: '320px',
        background: '#2d3748',
        borderRadius: '20px',
        padding: '20px',
        boxShadow: '0 25px 50px -12px rgba(0,0,0,0.5)',
        border: '8px solid #4a5568'
      }}>
        {/* Écran du téléphone */}
        <div style={{
          background: '#f7fafc',
          borderRadius: '4px',
          padding: '16px',
          minHeight: '300px',
          fontFamily: 'monospace',
          fontSize: '14px',
          color: '#1a202c',
          position: 'relative'
        }}>
          {/* Header opérateur */}
          <div style={{
            background: '#4299e1',
            color: 'white',
            padding: '8px 12px',
            margin: '-16px -16px 16px -16px',
            borderRadius: '4px 4px 0 0',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            fontSize: '12px'
          }}>
            <span>📶 MTN 4G</span>
            <span>🔋 78%</span>
          </div>

          {/* Heure */}
          <div style={{
            textAlign: 'center',
            fontSize: '24px',
            marginBottom: '20px',
            fontWeight: 'bold',
            color: '#2d3748'
          }}>
            {new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
          </div>

          {/* Notification SMS */}
          {status === 'received' && rideRequest && (
            <div style={{
              background: '#e6fffa',
              border: '2px solid #38b2ac',
              borderRadius: '8px',
              padding: '12px',
              marginBottom: '16px',
              animation: 'pulse 2s infinite'
            }}>
              <div style={{
                fontSize: '12px',
                color: '#2d3748',
                marginBottom: '8px',
                fontWeight: 'bold',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}>
                <span>📩</span>
                <span>NOUVEAU MESSAGE</span>
                <span style={{ marginLeft: 'auto', fontSize: '10px' }}>SafeRide</span>
              </div>
              <div style={{
                background: 'white',
                padding: '12px',
                borderRadius: '6px',
                borderLeft: '4px solid #38b2ac',
                lineHeight: '1.6'
              }}>
                <strong style={{ color: '#2d3748' }}>
                  {lang === 'fr' ? '🚗 NOUVELLE COURSE !' : '🚗 NEW RIDE!'}
                </strong>
                <br /><br />
                {lang === 'fr' ? (
                  <>
                    De: <strong>{rideRequest.pickup}</strong><br />
                    Vers: <strong>{rideRequest.destination}</strong><br />
                    Prix: <strong>{rideRequest.fare?.toLocaleString()} FCFA</strong><br />
                    Passager: {rideRequest.passenger}<br />
                    <br />
                    Répondez OUI pour accepter<br />
                    ou NON pour refuser<br />
                    <span style={{ color: '#e53e3e' }}>
                      ⏱️ {formatTime(timeLeft)} restantes
                    </span>
                  </>
                ) : (
                  <>
                    From: <strong>{rideRequest.pickup}</strong><br />
                    To: <strong>{rideRequest.destination}</strong><br />
                    Fare: <strong>{rideRequest.fare?.toLocaleString()} FCFA</strong><br />
                    Passenger: {rideRequest.passenger}<br />
                    <br />
                    Reply YES to accept<br />
                    or NO to decline<br />
                    <span style={{ color: '#e53e3e' }}>
                      ⏱️ {formatTime(timeLeft)} left
                    </span>
                  </>
                )}
              </div>
            </div>
          )}

          {status === 'accepted' && (
            <div style={{
              background: '#c6f6d5',
              border: '2px solid #48bb78',
              borderRadius: '8px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '48px', marginBottom: '12px' }}>✅</div>
              <strong style={{ color: '#22543d' }}>
                {lang === 'fr' ? 'COURSE ACCEPTÉE !' : 'RIDE ACCEPTED!'}
              </strong>
              <p style={{ fontSize: '12px', marginTop: '8px', color: '#2f855a' }}>
                {lang === 'fr' 
                  ? 'Allez chercher le passager.' 
                  : 'Go pick up the passenger.'}
              </p>
            </div>
          )}

          {status === 'rejected' && (
            <div style={{
              background: '#fed7d7',
              border: '2px solid #f56565',
              borderRadius: '8px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '48px', marginBottom: '12px' }}>❌</div>
              <strong style={{ color: '#c53030' }}>
                {lang === 'fr' ? 'COURSE REFUSÉE' : 'RIDE DECLINED'}
              </strong>
              <p style={{ fontSize: '12px', marginTop: '8px', color: '#c53030' }}>
                {lang === 'fr' 
                  ? 'Une autre course arrivera.' 
                  : 'Another ride will come.'}
              </p>
            </div>
          )}

          {status === 'timeout' && (
            <div style={{
              background: '#feebc8',
              border: '2px solid #ed8936',
              borderRadius: '8px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '48px', marginBottom: '12px' }}>⏰</div>
              <strong style={{ color: '#c05621' }}>
                {lang === 'fr' ? 'TEMPS ÉCOULÉ' : 'TIME EXPIRED'}
              </strong>
              <p style={{ fontSize: '12px', marginTop: '8px', color: '#c05621' }}>
                {lang === 'fr' 
                  ? 'La course a été annulée.' 
                  : 'The ride was cancelled.'}
              </p>
            </div>
          )}

          {/* Boutons du téléphone */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '12px',
            marginTop: '20px'
          }}>
            {status === 'received' && (
              <>
                <button
                  onClick={handleAccept}
                  style={{
                    background: '#48bb78',
                    color: 'white',
                    border: 'none',
                    padding: '16px',
                    borderRadius: '8px',
                    fontWeight: 'bold',
                    cursor: 'pointer',
                    fontSize: '16px'
                  }}
                >
                  ✓ {lang === 'fr' ? 'OUI' : 'YES'}
                </button>
                <button
                  onClick={handleReject}
                  style={{
                    background: '#f56565',
                    color: 'white',
                    border: 'none',
                    padding: '16px',
                    borderRadius: '8px',
                    fontWeight: 'bold',
                    cursor: 'pointer',
                    fontSize: '16px'
                  }}
                >
                  ✗ {lang === 'fr' ? 'NON' : 'NO'}
                </button>
              </>
            )}
            
            {status !== 'received' && (
              <button
                onClick={onClose}
                style={{
                  gridColumn: '1 / -1',
                  background: '#4a5568',
                  color: 'white',
                  border: 'none',
                  padding: '16px',
                  borderRadius: '8px',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                {lang === 'fr' ? 'FERMER' : 'CLOSE'}
              </button>
            )}
          </div>

          {/* Info hackathon */}
          <div style={{
            marginTop: '16px',
            padding: '8px',
            background: '#edf2f7',
            borderRadius: '4px',
            fontSize: '10px',
            color: '#718096',
            textAlign: 'center'
          }}>
            {lang === 'fr' 
              ? '📱 Simulation SMS pour le hackathon - En production : vrai SMS via Twilio/AfricasTalking'
              : '📱 SMS simulation for hackathon - In production: real SMS via Twilio/AfricasTalking'}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.02); }
        }
      `}</style>
    </div>
  )
}
