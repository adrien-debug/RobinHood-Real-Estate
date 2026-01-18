'use client'

import { useEffect, useState } from 'react'
import { Card, CardTitle, CardSubtitle } from '@/components/ui/Card'
import { KpiCard, KpiGrid } from '@/components/ui/KpiCard'
import { LoadingPage } from '@/components/ui/Loading'
import { BarChart, LineChart, PieChart, AreaChart, ScatterChart, GaugeChart } from '@/components/charts'
import { formatCompact, formatPercent, formatCurrency } from '@/lib/utils'
import { 
  TrendingUp, 
  DollarSign, 
  Building2, 
  Target,
  Activity,
  BarChart3,
  Percent
} from 'lucide-react'
import { useAutoRefresh } from '@/lib/useAutoRefresh'

interface OverviewData {
  dashboard: any
  zones: any
  opportunities: any
  transactions: any
  insights: any
}

export default function OverviewPage() {
  const AUTO_REFRESH_MS = 5000
  const [data, setData] = useState<OverviewData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAllData()
  }, [])

  const fetchAllData = async () => {
    try {
      setLoading(true)
      setError(null)

      const [dashRes, zonesRes, oppsRes, txRes, insightsHistRes, insightsZonesRes] = await Promise.all([
        fetch('/api/dashboard').then(r => r.json()),
        fetch('/api/zones').then(r => r.json()),
        fetch('/api/opportunities?limit=10').then(r => r.json()),
        fetch('/api/transactions?limit=20').then(r => r.json()),
        fetch('/api/transactions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'get_historical', days: 90 })
        }).then(r => r.json()),
        fetch('/api/zones').then(r => r.json())
      ])

      setData({
        dashboard: dashRes,
        zones: zonesRes,
        opportunities: oppsRes,
        transactions: txRes,
        insights: {
          historical: insightsHistRes.historical || [],
          zones: insightsZonesRes.zones || []
        }
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
      console.error('Overview fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  useAutoRefresh({
    intervalMs: AUTO_REFRESH_MS,
    onTick: fetchAllData
  })

  if (loading && !data) return <LoadingPage />
  if (error) return <div className="text-danger p-4">{error}</div>
  if (!data) return null

  const { dashboard, zones, opportunities, transactions, insights } = data

  // Prepare chart data
  const neighborhoodsChartData = dashboard.top_neighborhoods?.slice(0, 10).map((n: any) => ({
    name: n.community?.slice(0, 15) || 'N/A',
    value: n.transaction_count
  })) || []

  const propertyTypesChartData = dashboard.property_types?.by_rooms?.map((p: any) => ({
    name: p.rooms_bucket,
    value: p.count
  })) || []

  const strategyData = opportunities.opportunities?.reduce((acc: any, opp: any) => {
    const s = opp.recommended_strategy || 'OTHER'
    acc[s] = (acc[s] || 0) + 1
    return acc
  }, {}) || {}

  const strategyChartData = Object.entries(strategyData).map(([name, value]) => ({
    name,
    value
  }))

  const priceHistoryData = insights.historical?.map((h: any) => ({
    name: h.week.slice(5),
    price: h.avg_price,
    volume: h.volume
  })) || []

  const zonesChartData = zones.zones?.slice(0, 10).map((z: any) => ({
    name: z.community.slice(0, 12),
    price: z.avg_price_sqft,
    volume: z.transaction_count
  })) || []

  const scatterData = transactions.transactions?.filter((t: any) => t.area_sqft && t.price_per_sqft).map((t: any) => ({
    area: t.area_sqft,
    price: t.price_per_sqft,
    name: t.community
  })) || []

  // Calculate RSI
  const calculateRSI = () => {
    const historical = insights.historical || []
    if (historical.length < 14) return 50
    const prices = historical.map((h: any) => h.avg_price)
    let gains = 0, losses = 0
    for (let i = 1; i < prices.length; i++) {
      const change = prices[i] - prices[i-1]
      if (change > 0) gains += change
      else losses += Math.abs(change)
    }
    const avgGain = gains / prices.length
    const avgLoss = losses / prices.length
    if (avgLoss === 0) return 100
    const rs = avgGain / avgLoss
    return 100 - (100 / (1 + rs))
  }

  const rsi = calculateRSI()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Complete Overview</h1>
        <p className="text-text-muted text-sm mt-1">
          Toutes les données disponibles en temps réel (refresh 5s)
        </p>
      </div>

      {/* Section 1: Dashboard KPIs */}
      <div className="section-title">Dashboard KPIs</div>
      <KpiGrid>
        <KpiCard
          title="Last Day"
          subtitle="Transactions"
          value={dashboard.kpis?.transactions_last_day || 0}
          icon={<Building2 className="w-5 h-5" />}
          showLive
        />
        <KpiCard
          title="7 Days"
          subtitle="Transactions"
          value={dashboard.kpis?.transactions_7d || 0}
          icon={<TrendingUp className="w-5 h-5" />}
          showLive
        />
        <KpiCard
          title="30 Days"
          subtitle="Transactions"
          value={dashboard.kpis?.transactions_30d || 0}
          showLive
        />
        <KpiCard
          title="Volume 30D"
          subtitle="AED"
          value={formatCompact(dashboard.kpis?.volume_30d || 0)}
          icon={<DollarSign className="w-5 h-5" />}
          showLive
        />
        <KpiCard
          title="Median Price"
          subtitle="AED/sqft"
          value={Math.round(dashboard.kpis?.median_price_sqft || 0).toLocaleString()}
          showLive
        />
        <KpiCard
          title="Trend 7D"
          subtitle="vs prev week"
          value={formatPercent(dashboard.kpis?.variation_7d_pct || 0, true)}
          trend={dashboard.kpis?.variation_7d_pct}
          color={(dashboard.kpis?.variation_7d_pct || 0) > 0 ? 'success' : (dashboard.kpis?.variation_7d_pct || 0) < 0 ? 'danger' : 'default'}
          showLive
        />
      </KpiGrid>

      {/* Section 2: Market Activity */}
      <div className="section-title">Market Activity</div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardTitle>Top Neighborhoods</CardTitle>
          <CardSubtitle>30 day transaction volume</CardSubtitle>
          <BarChart 
            data={neighborhoodsChartData}
            dataKey="value"
            xAxisKey="name"
            horizontal
            height={350}
            showLabels
          />
        </Card>

        <Card>
          <CardTitle>Property Types</CardTitle>
          <CardSubtitle>Distribution by rooms</CardSubtitle>
          <BarChart 
            data={propertyTypesChartData}
            dataKey="value"
            xAxisKey="name"
            height={350}
            colors={['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']}
          />
        </Card>
      </div>

      {/* Section 3: Opportunities */}
      <div className="section-title">Investment Opportunities</div>
      <KpiGrid className="grid-cols-2 md:grid-cols-5">
        <KpiCard
          title="Total"
          subtitle="Opportunities"
          value={opportunities.stats?.total || 0}
          icon={<Target className="w-5 h-5" />}
          color="accent"
          showLive
        />
        <KpiCard
          title="FLIP"
          subtitle="Strategy"
          value={opportunities.stats?.by_strategy?.FLIP || 0}
          color="success"
          showLive
        />
        <KpiCard
          title="RENT"
          subtitle="Strategy"
          value={opportunities.stats?.by_strategy?.RENT || 0}
          color="info"
          showLive
        />
        <KpiCard
          title="Avg Score"
          subtitle="Quality"
          value={`${Math.round(opportunities.stats?.avg_score || 0)}%`}
          color="success"
          showLive
        />
        <KpiCard
          title="Avg Discount"
          subtitle="Below market"
          value={formatPercent(opportunities.stats?.avg_discount || 0)}
          showLive
        />
      </KpiGrid>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardTitle>Strategy Distribution</CardTitle>
          <PieChart 
            data={strategyChartData}
            height={300}
            centerLabel={opportunities.stats?.total || 0}
            colors={['#10B981', '#3B82F6', '#F59E0B', '#6B7280']}
          />
        </Card>

        <Card>
          <CardTitle>Top Opportunities</CardTitle>
          <CardSubtitle>Highest scoring deals</CardSubtitle>
          <div className="table-container mt-4">
            <table className="table">
              <thead>
                <tr>
                  <th>Location</th>
                  <th>Type</th>
                  <th>Score</th>
                  <th>Discount</th>
                </tr>
              </thead>
              <tbody>
                {opportunities.opportunities?.slice(0, 8).map((opp: any, index: number) => (
                  <tr key={index}>
                    <td>
                      <div className="font-medium text-text-primary">{opp.community || 'N/A'}</div>
                      <div className="text-xs text-text-muted">{opp.building || ''}</div>
                    </td>
                    <td>{opp.rooms_bucket || 'N/A'}</td>
                    <td>
                      <div className="flex items-center gap-2">
                        <div className="progress w-16">
                          <div 
                            className="progress-bar bg-accent" 
                            style={{ width: `${opp.global_score}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium">{Math.round(opp.global_score || 0)}</span>
                      </div>
                    </td>
                    <td className="text-success">-{(opp.discount_pct || 0).toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      {/* Section 4: Market Insights */}
      <div className="section-title">Market Insights</div>
      <KpiGrid className="grid-cols-2 md:grid-cols-4">
        <KpiCard
          title="Market RSI"
          subtitle="Momentum indicator"
          value={Math.round(rsi)}
          color={rsi > 70 ? 'danger' : rsi < 30 ? 'success' : 'info'}
          icon={<Activity className="w-5 h-5" />}
          showLive
        />
        <KpiCard
          title="Total Volume"
          subtitle="Transactions"
          value={formatCompact(insights.historical?.reduce((sum: number, h: any) => sum + h.volume, 0) || 0)}
          icon={<BarChart3 className="w-5 h-5" />}
          showLive
        />
        <KpiCard
          title="Zones Analyzed"
          subtitle="With data"
          value={zones.zones?.length || 0}
          icon={<Building2 className="w-5 h-5" />}
          showLive
        />
        <KpiCard
          title="Avg Opportunity"
          subtitle="Score"
          value={Math.round(dashboard.kpis?.avg_opportunity_score || 0)}
          color="accent"
          showLive
        />
      </KpiGrid>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardTitle>Price Evolution</CardTitle>
          <CardSubtitle>Last 90 days weekly data</CardSubtitle>
          <LineChart
            data={priceHistoryData}
            lines={[
              { dataKey: 'price', color: '#10B981', name: 'Avg Price' },
              { dataKey: 'volume', color: '#3B82F6', name: 'Volume', strokeDasharray: '5 5' }
            ]}
            xAxisKey="name"
            height={300}
            showLegend
          />
        </Card>

        <Card>
          <CardTitle>Zone Performance</CardTitle>
          <CardSubtitle>Top 10 zones by price</CardSubtitle>
          <BarChart
            data={zonesChartData}
            dataKey="price"
            xAxisKey="name"
            height={300}
            color="#10B981"
            showLabels
          />
        </Card>
      </div>

      {/* Section 5: Transactions */}
      <div className="section-title">Recent Transactions</div>
      <Card>
        <CardTitle>Latest Sales</CardTitle>
        <CardSubtitle>Last 20 transactions</CardSubtitle>
        <div className="table-container mt-4">
          <table className="table">
            <thead>
              <tr>
                <th>Location</th>
                <th>Type</th>
                <th>Area</th>
                <th>Price</th>
                <th>AED/sqft</th>
              </tr>
            </thead>
            <tbody>
              {transactions.transactions?.slice(0, 20).map((tx: any, index: number) => (
                <tr key={index}>
                  <td>
                    <div className="font-medium text-text-primary">{tx.community || 'N/A'}</div>
                    <div className="text-xs text-text-muted">{tx.building || ''}</div>
                  </td>
                  <td>{tx.rooms_bucket || 'N/A'}</td>
                  <td>{tx.area_sqft ? `${Math.round(tx.area_sqft)} sqft` : 'N/A'}</td>
                  <td>{formatCurrency(tx.price_aed || 0)}</td>
                  <td>{tx.price_per_sqft ? Math.round(tx.price_per_sqft).toLocaleString() : 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Section 6: Price vs Size */}
      <Card>
        <CardTitle>Price vs Size Correlation</CardTitle>
        <CardSubtitle>Area (sqft) vs Price per sqft</CardSubtitle>
        <ScatterChart
          data={scatterData}
          xKey="area"
          yKey="price"
          xLabel="Area (sqft)"
          yLabel="Price/sqft"
          height={300}
        />
      </Card>

      {/* Section 7: Market Regimes */}
      <div className="section-title">Market Regimes</div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {dashboard.regimes?.slice(0, 4).map((r: any, index: number) => (
          <Card key={index}>
            <div className="text-sm font-semibold text-text-primary truncate">{r.community}</div>
            <div className="mt-2 flex items-center justify-between">
              <span className="text-xs text-text-muted">{r.regime}</span>
              <span className="text-xs text-text-muted">{Math.round((r.confidence_score || 0) * 100)}%</span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
