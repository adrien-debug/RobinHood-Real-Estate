'use client'

import { useState } from 'react'
import FloorplanViewer from '@/components/FloorplanViewer'
import { Building2 } from 'lucide-react'

const locations = [
  { id: 10, name: 'Dubai Marina' },
  { id: 36, name: 'Downtown Dubai' },
  { id: 21741, name: 'Palm Jumeirah' },
  { id: 59, name: 'Business Bay' },
  { id: 72, name: 'JBR' },
  { id: 16770, name: 'Dubai Hills' },
  { id: 11, name: 'Arabian Ranches' },
  { id: 87107, name: 'Dubai Creek Harbour' },
]

export default function FloorplansPage() {
  const [selectedLocation, setSelectedLocation] = useState<number>(10) // Dubai Marina par défaut

  return (
    <div className="h-[calc(100vh-10rem)] flex flex-col space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Building2 className="w-6 h-6 text-accent" />
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Plans 2D/3D</h1>
            <p className="text-text-muted text-sm mt-1">Visualisation des propriétés à Dubai</p>
          </div>
        </div>
        <select
          value={selectedLocation}
          onChange={(e) => setSelectedLocation(parseInt(e.target.value))}
          className="bg-background-secondary border border-border rounded-lg px-4 py-2 text-sm text-text-primary focus:outline-none focus:border-accent"
        >
          {locations.map((loc) => (
            <option key={loc.id} value={loc.id}>
              {loc.name}
            </option>
          ))}
        </select>
      </div>

      {/* Viewer */}
      <div className="flex-1 overflow-hidden">
        <FloorplanViewer locationId={selectedLocation} />
      </div>
    </div>
  )
}
