"use client"

import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet"
import L from "leaflet"
import "leaflet/dist/leaflet.css"
import type { ServiceRequest } from "@/lib/types"

// Fix default marker icons in bundled builds
const defaultIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

L.Marker.prototype.options.icon = defaultIcon

interface LeafletMapProps {
  requests: ServiceRequest[]
}

export default function LeafletMap({ requests }: LeafletMapProps) {
  const markers = requests.filter(
    (r) => r.latitude != null && r.longitude != null
  )

  return (
    <MapContainer
      center={[37.5407, -77.436]}
      zoom={12}
      className="h-full w-full rounded-lg"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {markers.map((req) => (
        <Marker
          key={req.id}
          position={[req.latitude!, req.longitude!]}
        >
          <Popup>
            <div className="text-sm">
              <p className="font-semibold">{req.reference_number}</p>
              <p className="capitalize">{req.category}</p>
              {req.location && <p>{req.location}</p>}
              <p className="text-xs text-muted-foreground mt-1">
                Urgency: {req.urgency}/5
              </p>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}
