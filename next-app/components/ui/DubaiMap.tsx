'use client'

import { useEffect, useState, useMemo } from 'react'
import { Card, CardTitle, CardSubtitle } from '@/components/ui/Card'
import dynamic from 'next/dynamic'

// Coordonnées des communautés Dubai
const DUBAI_COMMUNITIES: Record<string, [number, number]> = {
  'Palm Jumeirah': [25.1124, 55.1384],
  'Dubai Marina': [25.0805, 55.1425],
  'Downtown Dubai': [25.1972, 55.2744],
  'Business Bay': [25.1850, 55.2614],
  'JBR': [25.0780, 55.1330],
  'DIFC': [25.2100, 55.2805],
  'JVC': [25.0650, 55.2100],
  'Jumeirah Village Circle': [25.0650, 55.2100],
  'JLT': [25.0750, 55.1480],
  'Jumeirah Lake Towers': [25.0750, 55.1480],
  'Sports City': [25.0350, 55.2200],
  'Dubai Hills': [25.1050, 55.2450],
  'Dubai Hills Estate': [25.1050, 55.2450],
  'Arabian Ranches': [25.0450, 55.2650],
  'Dubai Silicon Oasis': [25.1180, 55.3780],
  'International City': [25.1650, 55.4100],
  'Dubai South': [24.9350, 55.1650],
  'Damac Hills': [25.0150, 55.2350],
  'MBR City': [25.1650, 55.3150],
  'Mohammed Bin Rashid City': [25.1650, 55.3150],
  'Al Barsha': [25.1150, 55.2050],
  'Mirdif': [25.2250, 55.4250],
  'Discovery Gardens': [25.0450, 55.1350],
  'Motor City': [25.0450, 55.2350],
  'Town Square': [25.0250, 55.2650],
  'Arjan': [25.0550, 55.2350],
  'Al Furjan': [25.0350, 55.1450],
  'Dubai Creek Harbour': [25.2050, 55.3450],
  'Emaar Beachfront': [25.0850, 55.1350],
  'Sobha Hartland': [25.1750, 55.3050],
}

const DUBAI_CENTER: [number, number] = [25.1, 55.2]
const DEFAULT_ZOOM = 11

interface MapPoint {
  name: string
  price: number
  volume: number
  volatility?: number
}

interface DubaiMapProps {
  points: MapPoint[]
  height?: number
  onPointClick?: (name: string) => void
}

const MapContainer = dynamic(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { ssr: false }
)
const TileLayer = dynamic(
  () => import('react-leaflet').then((mod) => mod.TileLayer),
  { ssr: false }
)
const CircleMarker = dynamic(
  () => import('react-leaflet').then((mod) => mod.CircleMarker),
  { ssr: false }
)
const Tooltip = dynamic(
  () => import('react-leaflet').then((mod) => mod.Tooltip),
  { ssr: false }
)

function MapContent({ points, onPointClick }: { points: MapPoint[]; onPointClick?: (name: string) => void }) {
  const maxPrice = useMemo(() => Math.max(...points.map(p => p.price), 1), [points])
  const minPrice = useMemo(() => Math.min(...points.map(p => p.price), 0), [points])
  const maxVolume = useMemo(() => Math.max(...points.map(p => p.volume), 1), [points])

  const getColor = (price: number) => {
    const ratio = (price - minPrice) / (maxPrice - minPrice || 1)
    if (ratio > 0.7) return '#22C55E' // Vert vif
    if (ratio > 0.4) return '#3B82F6' // Bleu vif
    return '#F59E0B' // Ambre vif
  }

  const getRadius = (volume: number) => {
    const base = 8
    const scale = (volume / maxVolume) * 12
    return base + scale
  }

  return (
    <>
      <TileLayer
        attribution='&copy; <a href="https://carto.com/">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
      />
      {points.map((point) => {
        const coords = DUBAI_COMMUNITIES[point.name]
        if (!coords) return null

        return (
          <CircleMarker
            key={point.name}
            center={coords}
            radius={getRadius(point.volume)}
            pathOptions={{
              color: getColor(point.price),
              fillColor: getColor(point.price),
              fillOpacity: 0.8,
              weight: 2
            }}
            eventHandlers={{
              click: () => onPointClick?.(point.name)
            }}
          >
            <Tooltip direction="top" offset={[0, -10]} opacity={1}>
              <div className="text-xs font-medium">
                <div className="font-bold text-gray-900">{point.name}</div>
                <div className="text-gray-700">{Math.round(point.price).toLocaleString()} AED/sqft</div>
                <div className="text-gray-600">{point.volume} transactions</div>
              </div>
            </Tooltip>
          </CircleMarker>
        )
      })}
    </>
  )
}

export function DubaiMap({ points, height = 400, onPointClick }: DubaiMapProps) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const legend = [
    { label: 'Premium', color: '#22C55E' },
    { label: 'Mid-market', color: '#3B82F6' },
    { label: 'Affordable', color: '#F59E0B' }
  ]

  if (!mounted) {
    return (
      <Card>
        <CardTitle>Dubai Market Map</CardTitle>
        <CardSubtitle>Chargement...</CardSubtitle>
        <div style={{ height }} className="bg-background-secondary rounded-lg animate-pulse" />
      </Card>
    )
  }

  return (
    <Card className="overflow-hidden">
      <div className="flex items-center justify-between mb-4">
        <div>
          <CardTitle>Dubai Market Map</CardTitle>
          <CardSubtitle>Cliquez sur une zone</CardSubtitle>
        </div>
        <div className="flex items-center gap-3">
          {legend.map((item) => (
            <div key={item.label} className="flex items-center gap-1.5">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: item.color }}
              />
              <span className="text-xs text-text-muted">{item.label}</span>
            </div>
          ))}
        </div>
      </div>
      <div style={{ height }} className="rounded-lg overflow-hidden border border-border">
        <MapContainer
          center={DUBAI_CENTER}
          zoom={DEFAULT_ZOOM}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={true}
        >
          <MapContent points={points} onPointClick={onPointClick} />
        </MapContainer>
      </div>
    </Card>
  )
}
