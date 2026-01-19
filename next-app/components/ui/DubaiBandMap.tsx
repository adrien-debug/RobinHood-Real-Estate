'use client'

import { Card, CardSubtitle, CardTitle } from '@/components/ui/Card'

interface DubaiBandPoint {
  name: string
  price: number
  volume: number
}

interface DubaiBandMapProps {
  points: DubaiBandPoint[]
}

export function DubaiBandMap({ points }: DubaiBandMapProps) {
  const maxPrice = points.length ? Math.max(...points.map(p => p.price)) : 1
  const minPrice = points.length ? Math.min(...points.map(p => p.price)) : 0
  const maxVolume = points.length ? Math.max(...points.map(p => p.volume)) : 1

  const getTop = (price: number) => {
    if (maxPrice === minPrice) return 50
    const ratio = (price - minPrice) / (maxPrice - minPrice)
    return 70 - Math.round(ratio * 40)
  }

  return (
    <Card>
      <CardTitle>Dubai Band Map</CardTitle>
      <CardSubtitle>Points dynamiques (survol pour détails)</CardSubtitle>
      <div className="mt-5 relative h-48 rounded-2xl border border-border bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 overflow-hidden">
        <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_top_left,rgba(16,185,129,0.3),transparent_40%),radial-gradient(circle_at_bottom_right,rgba(59,130,246,0.35),transparent_45%)]" />
        <div className="absolute left-6 right-6 top-1/2 -translate-y-1/2 h-6 rounded-full bg-gradient-to-r from-blue-500/20 via-amber-500/30 to-emerald-500/20 border border-border/60" />
        {points.map((point, index) => {
          const left = points.length <= 1 ? 50 : 8 + (index / (points.length - 1)) * 84
          const top = getTop(point.price)
          const size = 8 + Math.round((point.volume / maxVolume) * 10)
          return (
            <div
              key={point.name}
              className="absolute rounded-full bg-accent shadow-[0_0_16px_rgba(16,185,129,0.6)]"
              style={{
                left: `${left}%`,
                top: `${top}%`,
                width: `${size}px`,
                height: `${size}px`,
                transform: 'translate(-50%, -50%)'
              }}
              title={`${point.name} • ${Math.round(point.price).toLocaleString()} AED/sqft • ${point.volume} tx`}
            />
          )
        })}
      </div>
      <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-2 text-xs text-text-muted">
        {points.map(point => (
          <div key={point.name} className="truncate">
            {point.name}
          </div>
        ))}
      </div>
    </Card>
  )
}
