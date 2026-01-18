'use client'

import { useEffect, useState } from 'react'
import { KpiCard, KpiGrid } from '@/components/ui/KpiCard'
import { Card, CardTitle, CardSubtitle } from '@/components/ui/Card'
import { Badge, RegimeBadge, StrategyBadge } from '@/components/ui/Badge'
import { Loading, LoadingPage } from '@/components/ui/Loading'
import { DatePicker } from '@/components/ui/DatePicker'
import { Select } from '@/components/ui/Select'
import { BarChart, PieChart, AreaChart, ScatterChart, GaugeChart } from '@/components/charts'
import { formatCompact, formatPercent, formatCurrency, formatDateAPI } from '@/lib/utils'
import { 
  TrendingUp, 
  DollarSign, 
  Building2, 
  Target,
  AlertTriangle,
  Zap,
  RefreshCw,
  Clock
} from 'lucide-react'

interface DashboardData {
  kpis: {
    transactions_last_day: number
    transactions_7d: number
    transactions_30d: number
    volume_30d: number
    median_price_sqft: number
    avg_price_sqft: number
    variation_7d_pct: number
    avg_opportunity_score: number
  }
  latest_date?: string
  top_opportunities: Array<{
    id: number
    community: string
    building: string
    rooms_bucket: string
    global_score: number
    discount_pct: number
    recommended_strategy: string
    area_sqft: number
  }>
  top_neighborhoods: Array<{
    community: string
    transaction_count: number
    avg_price_sqft: number
  }>
  property_types: {
    by_rooms: Array<{
      rooms_bucket: string
      count: number
      avg_price_sqft: number
    }>
  }
  regimes: Array<{
    community: string
    regime: string
    confidence_score: number
  }>
  brief: {
    main_risk: string
    strategic_recommendation: string
  } | null
  target_date?: string
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedDate, setSelectedDate] = useState(formatDateAPI(new Date()))
  const [lastUpdated, setLastUpdated] = useState<string | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [refreshInterval, setRefreshInterval] = useState('5')

  const refreshOptions = [
    { value: '5', label: '5s' },
    { value: '30', label: '30s' },
    { value: '60', label: '60s' },
    { value: '120', label: '2 min' },
    { value: '300', label: '5 min' }
  ]

  useEffect(() => {
    fetchDashboard({ silent: false })
  }, [selectedDate])

  useEffect(() => {
    if (!autoRefresh) return
    const intervalMs = Number(refreshInterval) * 1000
    if (!Number.isFinite(intervalMs) || intervalMs <= 0) return
    const id = setInterval(() => {
      fetchDashboard({ silent: true })
    }, intervalMs)
    return () => clearInterval(id)
  }, [autoRefresh, refreshInterval, selectedDate])

  const fetchDashboard = async ({ silent }: { silent: boolean }) => {
    try {
      setError(null)
      if (silent) {
        setIsRefreshing(true)
      } else {
        setLoading(true)
      }
      const res = await fetch(`/api/dashboard?date=${selectedDate}`)
      if (!res.ok) throw new Error('Failed to fetch dashboard')
      const json = await res.json()
      setData(json)
      setLastUpdated(new Date().toISOString())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      if (silent) {
        setIsRefreshing(false)
      } else {
        setLoading(false)
      }
    }
  }

  if (loading && !data) return <LoadingPage />
  if (!data) return <div className="text-danger p-4">No dashboard data available</div>

  const { kpis, top_opportunities, top_neighborhoods, property_types, regimes, brief } = data
  const latestDateLabel = data.latest_date || data.target_date || 'N/A'
  const lastUpdatedLabel = lastUpdated
    ? new Date(lastUpdated).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    : '—'

  // Prepare chart data
  const neighborhoodsChartData = top_neighborhoods.slice(0, 10).map(n => ({
    name: n.community?.slice(0, 15) || 'N/A',
    value: n.transaction_count,
    price: n.avg_price_sqft
  }))

  const propertyTypesChartData = property_types.by_rooms.map(p => ({
    name: p.rooms_bucket,
    value: p.count
  }))

  const strategyData = top_opportunities.reduce((acc, opp) => {
    const s = opp.recommended_strategy || 'OTHER'
    acc[s] = (acc[s] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const strategyChartData = Object.entries(strategyData).map(([name, value]) => ({
    name,
    value
  }))

  const scoreDistribution = [
    { name: '0-40', value: top_opportunities.filter(o => o.global_score < 40).length },
    { name: '40-60', value: top_opportunities.filter(o => o.global_score >= 40 && o.global_score < 60).length },
    { name: '60-80', value: top_opportunities.filter(o => o.global_score >= 60 && o.global_score < 80).length },
    { name: '80+', value: top_opportunities.filter(o => o.global_score >= 80).length },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-text-primary">Live Monitoring</h1>
            <Badge variant={autoRefresh ? 'success' : 'default'}>
              {autoRefresh ? 'Live' : 'Paused'}
            </Badge>
          </div>
          <p className="text-text-muted text-sm mt-1">Dubai Market Overview</p>
        </div>
        <div className="flex items-center gap-3">
          <DatePicker 
            value={selectedDate}
            onChange={setSelectedDate}
            max={formatDateAPI(new Date())}
            className="w-40"
          />
          <Select
            value={refreshInterval}
            onChange={setRefreshInterval}
            options={refreshOptions}
            className="w-24"
          />
          <button
            onClick={() => fetchDashboard({ silent: true })}
            className="btn-secondary"
            disabled={isRefreshing}
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            {isRefreshing ? 'Refreshing' : 'Refresh'}
          </button>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className="btn-secondary"
          >
            {autoRefresh ? 'Pause' : 'Go Live'}
          </button>
        </div>
      </div>

      {error && (
        <div className="text-danger text-sm bg-danger/10 border border-danger/20 rounded-lg px-4 py-2">
          {error}
        </div>
      )}

      {/* Live Status */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="flex items-center justify-between">
          <div>
            <p className="text-xs text-text-muted">Mode</p>
            <p className="text-sm text-text-primary">Auto-refresh</p>
          </div>
          <Badge variant={autoRefresh ? 'success' : 'default'}>
            {autoRefresh ? 'On' : 'Off'}
          </Badge>
        </Card>
        <Card className="flex items-center justify-between">
          <div>
            <p className="text-xs text-text-muted">Refresh</p>
            <p className="text-sm text-text-primary">Every {refreshInterval}s</p>
          </div>
          <Clock className="w-4 h-4 text-text-muted" />
        </Card>
        <Card className="flex items-center justify-between">
          <div>
            <p className="text-xs text-text-muted">Last Update</p>
            <p className="text-sm text-text-primary">{lastUpdatedLabel}</p>
          </div>
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : 'text-text-muted'}`} />
        </Card>
        <Card className="flex items-center justify-between">
          <div>
            <p className="text-xs text-text-muted">Data Date</p>
            <p className="text-sm text-text-primary">{latestDateLabel}</p>
          </div>
          <Badge variant="info">Supabase</Badge>
        </Card>
      </div>

      {/* KPIs Row */}
      <KpiGrid>
        <KpiCard
          title="Last Day"
          subtitle="Transactions"
          value={kpis.transactions_last_day}
          icon={<Building2 className="w-5 h-5" />}
        />
        <KpiCard
          title="7 Days"
          subtitle="Transactions"
          value={kpis.transactions_7d}
          icon={<TrendingUp className="w-5 h-5" />}
        />
        <KpiCard
          title="30 Days"
          subtitle="Transactions"
          value={kpis.transactions_30d}
        />
        <KpiCard
          title="Volume 30D"
          subtitle="AED"
          value={formatCompact(kpis.volume_30d)}
          icon={<DollarSign className="w-5 h-5" />}
        />
        <KpiCard
          title="Median Price"
          subtitle="AED/sqft"
          value={Math.round(kpis.median_price_sqft).toLocaleString()}
        />
        <KpiCard
          title="Trend 7D"
          subtitle="vs prev week"
          value={formatPercent(kpis.variation_7d_pct, true)}
          trend={kpis.variation_7d_pct}
          color={kpis.variation_7d_pct > 0 ? 'success' : kpis.variation_7d_pct < 0 ? 'danger' : 'default'}
        />
      </KpiGrid>

      {/* Market Activity Section */}
      <div className="section-title">Market Activity</div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Neighborhoods */}
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

        {/* Property Types */}
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

      {/* Analytics Section */}
      <div className="section-title">Market Analytics</div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Score Distribution */}
        <Card>
          <CardTitle>Score Distribution</CardTitle>
          <BarChart 
            data={scoreDistribution}
            dataKey="value"
            xAxisKey="name"
            height={220}
            colors={['#EF4444', '#F59E0B', '#3B82F6', '#10B981']}
          />
        </Card>

        {/* Strategy Mix */}
        <Card className="flex flex-col">
          <CardTitle>Strategy Mix</CardTitle>
          <div className="flex-1 flex items-center justify-center">
            <PieChart 
              data={strategyChartData}
              height={220}
              centerLabel={top_opportunities.length}
              colors={['#10B981', '#3B82F6', '#F59E0B', '#6B7280']}
            />
          </div>
        </Card>

        {/* Quality Gauge */}
        <Card className="flex flex-col items-center justify-center">
          <CardTitle>Quality Score</CardTitle>
          <div className="flex-1 flex items-center justify-center">
            <GaugeChart 
              value={kpis.avg_opportunity_score || 75}
              size="lg"
              label="Avg Score"
            />
          </div>
        </Card>
      </div>

      {/* Opportunities & Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Opportunities */}
        <Card>
          <CardTitle>Top Opportunities</CardTitle>
          <CardSubtitle>Highest scoring deals</CardSubtitle>
          <div className="table-container mt-4">
            <table className="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Location</th>
                  <th>Type</th>
                  <th>Score</th>
                  <th>Discount</th>
                  <th>Strategy</th>
                </tr>
              </thead>
              <tbody>
                {top_opportunities.slice(0, 8).map((opp, index) => (
                  <tr key={opp.id}>
                    <td className="text-text-muted">{index + 1}</td>
                    <td>
                      <div className="font-medium text-text-primary">{opp.community}</div>
                      <div className="text-xs text-text-muted">{opp.building}</div>
                    </td>
                    <td>{opp.rooms_bucket}</td>
                    <td>
                      <div className="flex items-center gap-2">
                        <div className="progress w-16">
                          <div 
                            className="progress-bar bg-accent" 
                            style={{ width: `${opp.global_score}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium">{Math.round(opp.global_score)}</span>
                      </div>
                    </td>
                    <td className="text-success">-{opp.discount_pct?.toFixed(1)}%</td>
                    <td>
                      <StrategyBadge strategy={opp.recommended_strategy} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Regimes & Brief */}
        <div className="space-y-6">
          {/* Market Regimes */}
          <Card>
            <CardTitle>Market Regimes</CardTitle>
            <div className="space-y-2 mt-4">
              {regimes.slice(0, 4).map((r, index) => (
                <div 
                  key={index}
                  className="flex items-center justify-between p-3 bg-background-secondary rounded-lg"
                >
                  <span className="text-sm text-text-primary truncate max-w-[150px]">
                    {r.community}
                  </span>
                  <div className="flex items-center gap-2">
                    <RegimeBadge regime={r.regime} />
                    <span className="text-xs text-text-muted">
                      {Math.round((r.confidence_score || 0) * 100)}%
                    </span>
                  </div>
                </div>
              ))}
              {regimes.length === 0 && (
                <p className="text-text-muted text-sm">No regime data available</p>
              )}
            </div>
          </Card>

          {/* CIO Brief */}
          <Card accent accentColor="#00D9A3">
            <CardTitle>CIO Brief</CardTitle>
            {brief ? (
              <div className="space-y-4 mt-4">
                <div>
                  <div className="flex items-center gap-2 text-warning mb-1">
                    <AlertTriangle className="w-4 h-4" />
                    <span className="text-xs font-semibold uppercase">Risk</span>
                  </div>
                  <p className="text-sm text-text-secondary line-clamp-3">
                    {brief.main_risk}
                  </p>
                </div>
                <div>
                  <div className="flex items-center gap-2 text-info mb-1">
                    <Zap className="w-4 h-4" />
                    <span className="text-xs font-semibold uppercase">Action</span>
                  </div>
                  <p className="text-sm text-text-secondary line-clamp-3">
                    {brief.strategic_recommendation}
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-text-muted text-sm mt-4">No brief available</p>
            )}
          </Card>
        </div>
      </div>
    </div>
  )
}
