import { useEffect, useMemo } from 'react'
import { MapContainer, Marker, Polyline, Popup, TileLayer, useMap, useMapEvents } from 'react-leaflet'
import L from 'leaflet'

function divIcon(snapshot) {
  const cls =
    snapshot.status === 'reliable' ? '' : snapshot.status === 'attention' ? 'attention' : 'blocked'
  const initials = snapshot.driver.name.split(' ').map((n) => n[0]).slice(0, 2).join('')
  return L.divIcon({
    className: '',
    html: `<div class="driver-marker ${cls}" style="background:${snapshot.driver.avatar_color}">${initials}</div>`,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
  })
}

function pinIcon(color, label) {
  return L.divIcon({
    className: '',
    html: `<div class="driver-marker" style="background:${color};color:#06121a">${label}</div>`,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
  })
}

function ClickHandler({ onSetPickup, onSetDestination }) {
  useMapEvents({
    click(e) {
      if (e.originalEvent.shiftKey) onSetDestination([e.latlng.lat, e.latlng.lng])
      else onSetPickup([e.latlng.lat, e.latlng.lng])
    },
  })
  return null
}

function Recenter({ center }) {
  const map = useMap()
  useEffect(() => {
    if (center) map.flyTo(center, 13, { duration: 0.6 })
  }, [center, map])
  return null
}

export default function MapView({ center, pickup, destination, snapshots, onSetPickup, onSetDestination, onSelect }) {
  const allSnapshots = useMemo(() => snapshots ?? [], [snapshots])
  const route = useMemo(() => (pickup && destination ? [pickup, destination] : null), [pickup, destination])

  return (
    <MapContainer center={center} zoom={13} className="map" style={{ height: '100%', width: '100%' }} scrollWheelZoom>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Recenter center={center} />
      <ClickHandler onSetPickup={onSetPickup} onSetDestination={onSetDestination} />

      {pickup && (
        <Marker position={pickup} icon={pinIcon('#22d3ee', 'P')} />
      )}
      {destination && (
        <Marker position={destination} icon={pinIcon('#22c55e', 'D')} />
      )}
      {route && <Polyline positions={route} pathOptions={{ color: '#22d3ee', weight: 4, dashArray: '6 8', opacity: 0.8 }} />}

      {allSnapshots.map((snap) => (
        <Marker
          key={snap.driver.id}
          position={[snap.driver.current_location.lat, snap.driver.current_location.lng]}
          icon={divIcon(snap)}
          eventHandlers={{ click: () => onSelect && onSelect(snap) }}
        >
          <Popup>
            <strong>{snap.driver.name}</strong><br />
            {snap.driver.vehicle} · {snap.driver.plate}<br />
            Score: <strong>{snap.trust_score}</strong> ({snap.status})
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}
