'use client'

import { useEffect, useState } from 'react'
import { KpiCard, KpiGrid } from '@/components/ui/KpiCard'
import { Card, CardTitle, CardSubtitle } from '@/components/ui/Card'
import { LoadingPage } from '@/components/ui/Loading'
import { BarChart, AreaChart } from '@/components/charts'
import { formatPercent, formatCurrency } from '@/lib/utils'
import { Percent, TrendingUp, Building2 } from 'lucide-react'
import { useAutoRefresh } from '@/lib/useAutoRefresh'

interface YieldData {
  zones: Array<{
    community: string
    avg_price_sqft: number
    estimated_rent: number
    gross_yield: number
    transaction_count: number
    data_source?: string
    rent_data_available?: boolean
  }>
  summary: {
    avg_yield: number
    max_yield: number
    min_yield: number
    zones_with_real_data?: number
    zones_with_estimated_data?: number
    total_zones?: number
  }
}

export default function YieldPage() {
  const AUTO_REFRESH_MS = 5000
  const [data, setData] = useState<YieldData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchYieldData()
  }, [])

  const fetchYieldData = async () => {
    try {
      setLoading(true)
      const res = await fetch('/api/yield')
      const json = await res.json()
      
      if (json.error) {
        console.error('Yield API error:', json.error)
        return
      }

      // Map API response to component state
      const zonesWithYield = (json.zones || []).map((z: any) => ({
        community: z.community,
        avg_price_sqft: z.avg_price_sqft,
        estimated_rent: z.monthly_rent,
        gross_yield: z.gross_yield,
        transaction_count: z.transaction_count,
        data_source: z.data_source,
        rent_data_available: z.rent_data_available
      }))
      
      setData({
        zones: zonesWithYield,
        summary: json.summary
      })
    } catch (err) {
      console.error('Failed to fetch yield data:', err)
    } finally {
      setLoading(false)
    }
  }

  useAutoRefresh({
    intervalMs: AUTO_REFRESH_MS,
    onTick: fetchYieldData
  })

  if (loading && !data) return <LoadingPage />
  if (!data) return <div className="text-text-muted p-4">No data available</div>

  const { zones, summary } = data

  // Sort by yield for charts
  const sortedByYield = [...zones].sort((a, b) => b.gross_yield - a.gross_yield)
  
  const yieldChartData = sortedByYield.slice(0, 15).map(z => ({
    name: z.community.slice(0, 12),
    yield: z.gross_yield,
    price: z.avg_price_sqft / 100 // Scale for visibility
  }))

  const topYieldZones = sortedByYield.slice(0, 5)
  const lowYieldZones = sortedByYield.slice(-5).reverse()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Rental Yield Analysis</h1>
        <p className="text-text-muted text-sm mt-1">
          Gross yields by zone • {summary.zones_with_real_data || 0} zones with real rental data, {summary.zones_with_estimated_data || 0} estimated
        </p>
      </div>

      {/* KPIs */}
      <KpiGrid className="grid-cols-2 md:grid-cols-4">
        <KpiCard
          title="Average Yield"
          subtitle="All zones"
          value={formatPercent(summary.avg_yield)}
          icon={<Percent className="w-5 h-5" />}
          color="accent"
          showLive
        />
        <KpiCard
          title="Maximum Yield"
          subtitle="Best performer"
          value={formatPercent(summary.max_yield)}
          color="success"
          showLive
        />
        <KpiCard
          title="Minimum Yield"
          subtitle="Lowest"
          value={formatPercent(summary.min_yield)}
          color="warning"
          showLive
        />
        <KpiCard
          title="Zones Analyzed"
          subtitle="With data"
          value={zones.length}
          icon={<Building2 className="w-5 h-5" />}
          showLive
        />
      </KpiGrid>

      {/* Yield by Zone Chart */}
      <Card>
        <CardTitle>Gross Yield by Zone</CardTitle>
        <CardSubtitle>Top 15 zones by yield</CardSubtitle>
        <BarChart
          data={yieldChartData}
          dataKey="yield"
          xAxisKey="name"
          color="#10B981"
          height={350}
          horizontal
          showLabels
        />
      </Card>

      {/* Top & Low Yield Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Yield */}
        <Card accent accentColor="#10B981">
          <CardTitle>Top Yield Zones</CardTitle>
          <CardSubtitle>Best rental returns</CardSubtitle>
          <div className="table-container mt-4">
            <table className="table">
              <thead>
                <tr>
                  <th>Zone</th>
                  <th>Price/sqft</th>
                  <th>Est. Rent</th>
                  <th>Yield</th>
                </tr>
              </thead>
              <tbody>
                {topYieldZones.map((zone, index) => (
                  <tr key={index}>
                    <td>
                      <div className="font-medium text-text-primary">{zone.community}</div>
                      {zone.rent_data_available && (
                        <div className="text-xs text-success">✓ Real data</div>
                      )}
                    </td>
                    <td>{Math.round(zone.avg_price_sqft).toLocaleString()} AED</td>
                    <td>{Math.round(zone.estimated_rent).toLocaleString()} AED</td>
                    <td className="text-success font-semibold">
                      {formatPercent(zone.gross_yield)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Low Yield (Premium areas) */}
        <Card accent accentColor="#F59E0B">
          <CardTitle>Premium Zones</CardTitle>
          <CardSubtitle>Lower yield, higher appreciation potential</CardSubtitle>
          <div className="table-container mt-4">
            <table className="table">
              <thead>
                <tr>
                  <th>Zone</th>
                  <th>Price/sqft</th>
                  <th>Est. Rent</th>
                  <th>Yield</th>
                </tr>
              </thead>
              <tbody>
                {lowYieldZones.map((zone, index) => (
                  <tr key={index}>
                    <td className="font-medium text-text-primary">{zone.community}</td>
                    <td>{Math.round(zone.avg_price_sqft).toLocaleString()} AED</td>
                    <td>{Math.round(zone.estimated_rent).toLocaleString()} AED</td>
                    <td className="text-warning font-semibold">
                      {formatPercent(zone.gross_yield)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      {/* Yield vs Price Scatter */}
      <Card>
        <CardTitle>Yield vs Price Analysis</CardTitle>
        <CardSubtitle>Higher price zones typically have lower yields</CardSubtitle>
        <div className="h-[300px] flex items-center justify-center text-text-muted">
          <p>Inverse correlation: Premium areas (high price) tend to have lower yields but better capital appreciation.</p>
        </div>
      </Card>

      {/* All Zones Table */}
      <Card>
        <CardTitle>All Zones</CardTitle>
        <div className="table-container mt-4">
          <table className="table">
            <thead>
              <tr>
                <th>Zone</th>
                <th>Avg Price/sqft</th>
                <th>Est. Annual Rent</th>
                <th>Gross Yield</th>
                <th>Transactions</th>
              </tr>
            </thead>
            <tbody>
              {zones.map((zone, index) => (
                <tr key={index}>
                  <td>
                    <div className="font-medium text-text-primary">{zone.community}</div>
                    {zone.rent_data_available && (
                      <div className="text-xs text-success">✓ Real rental data</div>
                    )}
                  </td>
                  <td>{Math.round(zone.avg_price_sqft).toLocaleString()} AED</td>
                  <td>{Math.round(zone.estimated_rent * 12).toLocaleString()} AED</td>
                  <td className={zone.gross_yield >= 6 ? 'text-success' : zone.gross_yield >= 5 ? 'text-accent' : 'text-warning'}>
                    {formatPercent(zone.gross_yield)}
                  </td>
                  <td>{zone.transaction_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
