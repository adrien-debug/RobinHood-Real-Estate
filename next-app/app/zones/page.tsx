'use client'

import { useEffect, useState } from 'react'
import { KpiCard, KpiGrid } from '@/components/ui/KpiCard'
import { Card, CardTitle, CardSubtitle } from '@/components/ui/Card'
import { Select } from '@/components/ui/Select'
import { DatePicker } from '@/components/ui/DatePicker'
import { LoadingPage } from '@/components/ui/Loading'
import { Badge, RegimeBadge } from '@/components/ui/Badge'
import { AreaChart, BarChart, LineChart } from '@/components/charts'
import { formatPercent, formatDateAPI, getRegimeColor } from '@/lib/utils'
import { useAutoRefresh } from '@/lib/useAutoRefresh'

interface ZoneData {
  community: string
  avg_price_sqft: number
  transaction_count: number
  volatility?: number
}

interface ZoneDetailData {
  community: string
  baselines: Array<{
    rooms_bucket: string
    median_price_per_sqft: number
    transaction_count: number
    momentum: number
  }>
  regime: {
    regime: string
    confidence_score: number
    volume_trend: string
    price_trend: string
  } | null
  price_history: Array<{
    date: string
    avg_price: number
    count: number
  }>
}

export default function ZonesPage() {
  const AUTO_REFRESH_MS = 5000
  const [zones, setZones] = useState<ZoneData[]>([])
  const [communities, setCommunities] = useState<string[]>([])
  const [zoneDetail, setZoneDetail] = useState<ZoneDetailData | null>(null)
  const [loading, setLoading] = useState(true)
  
  const [selectedDate, setSelectedDate] = useState(formatDateAPI(new Date()))
  const [selectedZone, setSelectedZone] = useState('')

  useEffect(() => {
    fetchZones()
  }, [selectedDate])

  useEffect(() => {
    if (selectedZone) {
      fetchZoneDetail(selectedZone)
    }
  }, [selectedZone, selectedDate])

  const fetchZones = async () => {
    try {
      setLoading(true)
      const res = await fetch(`/api/zones?date=${selectedDate}`)
      const json = await res.json()
      setZones(json.zones || [])
      setCommunities(json.communities || [])
      if (json.communities?.length > 0 && !selectedZone) {
        setSelectedZone(json.communities[0])
      }
    } catch (err) {
      console.error('Failed to fetch zones:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchZoneDetail = async (community: string) => {
    try {
      const res = await fetch(`/api/zones?date=${selectedDate}&community=${encodeURIComponent(community)}`)
      const json = await res.json()
      setZoneDetail(json)
    } catch (err) {
      console.error('Failed to fetch zone detail:', err)
    }
  }

  useAutoRefresh({
    intervalMs: AUTO_REFRESH_MS,
    onTick: () => {
      fetchZones()
      if (selectedZone) fetchZoneDetail(selectedZone)
    },
    deps: [selectedDate, selectedZone]
  })

  if (loading && zones.length === 0) return <LoadingPage />

  const topPriceZone = zones[0]
  const topVolumeZone = [...zones].sort((a, b) => b.transaction_count - a.transaction_count)[0]
  const lowestVolatilityZone = [...zones].filter(z => z.volatility != null).sort((a, b) => (a.volatility || 0) - (b.volatility || 0))[0]

  // Heatmap data
  const heatmapData = zones.slice(0, 15).map(z => ({
    name: z.community.slice(0, 12),
    price: z.avg_price_sqft,
    volume: z.transaction_count
  }))

  // Price history chart data
  const priceHistoryData = zoneDetail?.price_history.map(p => ({
    name: p.date.slice(5), // MM-DD
    price: p.avg_price,
    volume: p.count
  })) || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Zone Analysis</h1>
          <p className="text-text-muted text-sm mt-1">Market performance by neighborhood</p>
        </div>
        <div className="flex items-center gap-3">
          <DatePicker 
            value={selectedDate}
            onChange={setSelectedDate}
            max={formatDateAPI(new Date())}
            className="w-40"
          />
          <Select
            value={selectedZone}
            onChange={setSelectedZone}
            options={communities.map(c => ({ value: c, label: c }))}
            placeholder="Select Zone"
            className="w-56"
          />
        </div>
      </div>

      {/* Zone Performance Heatmap */}
      <Card>
        <CardTitle>Zone Performance Heatmap</CardTitle>
        <CardSubtitle>Top 15 zones by average price</CardSubtitle>
        <BarChart
          data={heatmapData}
          dataKey="price"
          xAxisKey="name"
          color="#10B981"
          height={200}
          showLabels
        />
      </Card>

      {/* Top Zone Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <KpiCard
          title="Top Price Zone"
          subtitle={topPriceZone?.community || 'N/A'}
          value={topPriceZone ? Math.round(topPriceZone.avg_price_sqft).toLocaleString() : 'N/A'}
          color="success"
        />
        <KpiCard
          title="Top Volume Zone"
          subtitle={topVolumeZone?.community || 'N/A'}
          value={topVolumeZone?.transaction_count || 0}
          color="info"
        />
        <KpiCard
          title="Most Stable Zone"
          subtitle={lowestVolatilityZone?.community || 'N/A'}
          value={lowestVolatilityZone ? formatPercent((lowestVolatilityZone.volatility || 0) * 100) : 'N/A'}
          color="accent"
        />
      </div>

      {/* Selected Zone Detail */}
      {zoneDetail && (
        <>
          <div className="section-title flex items-center gap-4">
            <span>{zoneDetail.community}</span>
            {zoneDetail.regime && (
              <div className="flex items-center gap-2">
                <RegimeBadge regime={zoneDetail.regime.regime} />
                <span className="text-sm text-text-muted">
                  {Math.round((zoneDetail.regime.confidence_score || 0) * 100)}% confidence
                </span>
              </div>
            )}
          </div>

          {/* Metrics by Type */}
          {zoneDetail.baselines.length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {zoneDetail.baselines.slice(0, 4).map((b, index) => (
                <Card key={index} className="text-center">
                  <p className="text-xs text-text-muted uppercase tracking-wider mb-2">
                    {b.rooms_bucket}
                  </p>
                  <p className="text-2xl font-bold text-text-primary">
                    {Math.round(b.median_price_per_sqft || 0).toLocaleString()}
                  </p>
                  <p className="text-xs text-text-muted">AED/sqft</p>
                  <div className="mt-3 pt-3 border-t border-border flex justify-between text-xs">
                    <span className="text-text-muted">Momentum</span>
                    <span className={b.momentum > 0 ? 'text-success' : b.momentum < 0 ? 'text-danger' : 'text-text-muted'}>
                      {b.momentum > 0 ? '+' : ''}{((b.momentum || 0) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between text-xs mt-1">
                    <span className="text-text-muted">Volume</span>
                    <span className="text-text-primary">{b.transaction_count}</span>
                  </div>
                </Card>
              ))}
            </div>
          )}

          {/* Price Evolution Chart */}
          <Card>
            <CardTitle>Price Evolution</CardTitle>
            <CardSubtitle>Last 30 days</CardSubtitle>
            <LineChart
              data={priceHistoryData}
              lines={[
                { dataKey: 'price', color: '#10B981', name: 'Avg Price' }
              ]}
              xAxisKey="name"
              height={350}
            />
          </Card>

          {/* Investment Signals */}
          {zoneDetail.regime && (
            <Card accent accentColor={getRegimeColor(zoneDetail.regime.regime)}>
              <CardTitle>Investment Signals</CardTitle>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                <div className="p-4 bg-background-secondary rounded-lg">
                  <p className="text-xs text-text-muted uppercase mb-1">Volume Trend</p>
                  <p className="text-lg font-semibold text-text-primary">
                    {zoneDetail.regime.volume_trend || 'N/A'}
                  </p>
                </div>
                <div className="p-4 bg-background-secondary rounded-lg">
                  <p className="text-xs text-text-muted uppercase mb-1">Price Trend</p>
                  <p className="text-lg font-semibold text-text-primary">
                    {zoneDetail.regime.price_trend || 'N/A'}
                  </p>
                </div>
                <div className="p-4 bg-background-secondary rounded-lg">
                  <p className="text-xs text-text-muted uppercase mb-1">Regime</p>
                  <p className="text-lg font-semibold" style={{ color: getRegimeColor(zoneDetail.regime.regime) }}>
                    {zoneDetail.regime.regime}
                  </p>
                </div>
              </div>
            </Card>
          )}
        </>
      )}

      {/* All Zones Table */}
      <Card>
        <CardTitle>All Zones</CardTitle>
        <CardSubtitle>90 day performance summary</CardSubtitle>
        <div className="table-container mt-4">
          <table className="table">
            <thead>
              <tr>
                <th>Zone</th>
                <th>Avg Price</th>
                <th>Transactions</th>
                <th>Volatility</th>
              </tr>
            </thead>
            <tbody>
              {zones.map((zone, index) => (
                <tr 
                  key={index}
                  className={zone.community === selectedZone ? 'bg-accent/10' : ''}
                  onClick={() => setSelectedZone(zone.community)}
                  style={{ cursor: 'pointer' }}
                >
                  <td className="font-medium text-text-primary">{zone.community}</td>
                  <td>{Math.round(zone.avg_price_sqft).toLocaleString()} AED</td>
                  <td>{zone.transaction_count}</td>
                  <td>
                    <Badge 
                      variant={(zone.volatility || 0) > 0.25 ? 'danger' : (zone.volatility || 0) > 0.15 ? 'warning' : 'success'}
                    >
                      {formatPercent((zone.volatility || 0) * 100)}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
