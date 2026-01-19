'use client'

import { useEffect, useState } from 'react'
import { KpiCard, KpiGrid } from '@/components/ui/KpiCard'
import { Card, CardTitle, CardSubtitle } from '@/components/ui/Card'
import { AlertsBanner } from '@/components/ui/AlertsBanner'
import { ExportPdf } from '@/components/ui/ExportPdf'
import { Badge, RegimeBadge, StrategyBadge } from '@/components/ui/Badge'
import { LoadingPage } from '@/components/ui/Loading'
import { Select } from '@/components/ui/Select'
import { AreaChart, BarChart, PieChart } from '@/components/charts'
import { formatCompact, formatPercent, formatCurrency } from '@/lib/utils'
import {
  TrendingUp,
  DollarSign,
  Building2,
  AlertTriangle,
  RefreshCw,
  Percent
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
    id: string
    community: string
    building: string | null
    rooms_bucket: string
    global_score: number
    discount_pct: number
    recommended_strategy: string
  }>
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

interface ZoneData {
  community: string
  avg_price_sqft: number
  transaction_count: number
}

interface YieldSummary {
  summary: {
    avg_yield: number
    max_yield: number
    min_yield: number
    zones_with_real_data: number
    zones_with_estimated_data: number
    total_zones: number
  }
}

interface TransactionItem {
  community: string
  building: string | null
  rooms_bucket: string | null
  area_sqft: number | null
  price_aed: number | null
  price_per_sqft: number | null
}

interface HistoricalPoint {
  week: string
  avg_price: number
  volume: number
}

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null)
  const [zones, setZones] = useState<ZoneData[]>([])
  const [yieldData, setYieldData] = useState<YieldSummary | null>(null)
  const [transactions, setTransactions] = useState<TransactionItem[]>([])
  const [snapshotHistory, setSnapshotHistory] = useState<HistoricalPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<string | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [refreshInterval, setRefreshInterval] = useState('30')
  const [snapshotDays, setSnapshotDays] = useState('30')
  const [txDays, setTxDays] = useState('7')

  const refreshOptions = [
    { value: '5', label: '5s' },
    { value: '30', label: '30s' },
    { value: '60', label: '60s' },
    { value: '120', label: '2 min' },
    { value: '300', label: '5 min' }
  ]

  const snapshotOptions = [
    { value: '7', label: '7 jours' },
    { value: '30', label: '30 jours' },
    { value: '90', label: '90 jours' }
  ]

  const txOptions = [
    { value: '7', label: '7 jours' },
    { value: '30', label: '30 jours' }
  ]

  useEffect(() => {
    fetchDashboard({ silent: false })
  }, [snapshotDays, txDays])

  useEffect(() => {
    if (!autoRefresh) return
    const intervalMs = Number(refreshInterval) * 1000
    if (!Number.isFinite(intervalMs) || intervalMs <= 0) return
    const id = setInterval(() => {
      fetchDashboard({ silent: true })
    }, intervalMs)
    return () => clearInterval(id)
  }, [autoRefresh, refreshInterval, snapshotDays, txDays])

  const fetchDashboard = async ({ silent }: { silent: boolean }) => {
    try {
      setError(null)
      if (silent) {
        setIsRefreshing(true)
      } else {
        setLoading(true)
      }

      const [
        dashboardRes,
        zonesRes,
        yieldRes,
        txRes,
        snapshotRes
      ] = await Promise.all([
        fetch('/api/dashboard'),
        fetch('/api/zones'),
        fetch('/api/yield'),
        fetch(`/api/transactions?days=${txDays}&limit=20`),
        fetch('/api/transactions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'get_historical', days: parseInt(snapshotDays, 10) || 30 })
        })
      ])

      if (!dashboardRes.ok) throw new Error('Failed to fetch dashboard')

      const [
        dashboardJson,
        zonesJson,
        yieldJson,
        txJson,
        snapshotJson
      ] = await Promise.all([
        dashboardRes.json(),
        zonesRes.json(),
        yieldRes.json(),
        txRes.json(),
        snapshotRes.json()
      ])

      setDashboard(dashboardJson)
      setZones(zonesJson.zones || [])
      setYieldData(yieldJson)
      setTransactions(txJson.transactions || [])
      setSnapshotHistory(snapshotJson.historical || [])
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

  if (loading && !dashboard) return <LoadingPage />
  if (!dashboard) return <div className="text-danger p-4">No dashboard data available</div>

  const { kpis, top_opportunities, regimes, brief } = dashboard
  const latestDateLabel = dashboard.latest_date || dashboard.target_date || 'N/A'
  const lastUpdatedLabel = lastUpdated
    ? new Date(lastUpdated).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    : '—'

  const snapshotChartData = snapshotHistory.map(h => ({
    name: h.week.slice(5),
    price: h.avg_price,
    volume: h.volume
  }))

  const snapshotVolume = snapshotHistory.reduce((sum, h) => sum + h.volume, 0)
  const snapshotAvgPrice = snapshotHistory.length
    ? snapshotHistory.reduce((sum, h) => sum + h.avg_price, 0) / snapshotHistory.length
    : 0
  const snapshotTrend = snapshotHistory.length >= 6
    ? ((snapshotHistory[snapshotHistory.length - 1].avg_price - snapshotHistory[0].avg_price) / snapshotHistory[0].avg_price) * 100
    : 0

  const topZones = zones.slice(0, 16)
  const yieldSummary = yieldData?.summary

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Dashboard</h1>
          <p className="text-text-muted text-sm mt-1">
            Data: {latestDateLabel} • Refresh: {refreshInterval}s
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select
            value={refreshInterval}
            onChange={setRefreshInterval}
            options={refreshOptions}
            className="w-20"
          />
          <button
            onClick={() => fetchDashboard({ silent: true })}
            className="btn-secondary"
            disabled={isRefreshing}
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`btn-secondary ${autoRefresh ? 'bg-success/20 text-success' : ''}`}
          >
            {autoRefresh ? 'Live' : 'Paused'}
          </button>
          <ExportPdf targetId="dashboard-content" filename="dashboard-report" />
        </div>
      </div>

      {error && (
        <div className="text-danger text-sm bg-danger/10 border border-danger/20 rounded-lg px-4 py-2">
          {error}
        </div>
      )}

      <div id="dashboard-content">
      {/* KPI Summary */}
      <KpiGrid className="grid-cols-2 md:grid-cols-4">
        <KpiCard
          title="Last Day"
          subtitle="Transactions"
          value={kpis.transactions_last_day}
          icon={<Building2 className="w-5 h-5" />}
          showLive
        />
        <KpiCard
          title="7 Days"
          subtitle="Transactions"
          value={kpis.transactions_7d}
          icon={<TrendingUp className="w-5 h-5" />}
          showLive
        />
        <KpiCard
          title="30 Days"
          subtitle="Transactions"
          value={kpis.transactions_30d}
          showLive
        />
        <KpiCard
          title="Volume 30D"
          subtitle="AED"
          value={formatCompact(kpis.volume_30d)}
          icon={<DollarSign className="w-5 h-5" />}
          showLive
        />
      </KpiGrid>

      {/* Market Snapshot */}
      <Card>
        <div className="flex items-center justify-between flex-wrap gap-4 mb-6">
          <div>
            <CardTitle>Market Snapshot</CardTitle>
            <CardSubtitle>Prix + volumes avec filtre unique</CardSubtitle>
          </div>
          <Select
            value={snapshotDays}
            onChange={setSnapshotDays}
            options={snapshotOptions}
            className="w-36"
          />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="space-y-3">
            <div className="p-3 bg-background-secondary rounded-lg">
              <p className="text-xs text-text-muted">Prix moyen</p>
              <p className="text-lg font-semibold text-text-primary">
                {Math.round(snapshotAvgPrice).toLocaleString()} AED/sqft
              </p>
            </div>
            <div className="p-3 bg-background-secondary rounded-lg">
              <p className="text-xs text-text-muted">Volume total</p>
              <p className="text-lg font-semibold text-text-primary">
                {formatCompact(snapshotVolume)}
              </p>
            </div>
            <div className="p-3 bg-background-secondary rounded-lg">
              <p className="text-xs text-text-muted">Tendance prix</p>
              <p className="text-lg font-semibold text-text-primary">
                {formatPercent(snapshotTrend, true)}
              </p>
            </div>
          </div>
          <div className="lg:col-span-3 relative">
            {snapshotHistory.length > 1 ? (
              <AreaChart
                data={snapshotChartData}
                dataKey="price"
                xAxisKey="name"
                height={280}
                color="#10B981"
              />
            ) : (
              <div className="h-[280px] flex items-center justify-center bg-background-secondary/40 rounded-lg border border-border">
                <div className="text-center">
                  <p className="text-text-muted text-sm">Données insuffisantes pour afficher le graphique</p>
                  <p className="text-text-muted text-xs mt-1">{snapshotHistory.length} point(s) de données disponible(s)</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Zones + Yield */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardTitle>Top 16 Zones</CardTitle>
          <CardSubtitle>Prix moyen + volume (cliquez pour la carte)</CardSubtitle>
          <div className="mt-4 space-y-3">
            {topZones.map(zone => (
              <div key={zone.community} className="flex items-center justify-between">
                <div className="text-sm text-text-primary truncate max-w-[160px]">
                  {zone.community}
                </div>
                <div className="text-xs text-text-muted">
                  {Math.round(zone.avg_price_sqft).toLocaleString()} AED/sqft • {zone.transaction_count} tx
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Yield Summary</CardTitle>
              <CardSubtitle>Données réelles + estimées</CardSubtitle>
            </div>
            <Percent className="w-5 h-5 text-text-muted" />
          </div>
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-3 bg-background-secondary rounded-lg">
              <p className="text-xs text-text-muted">Rendement moyen</p>
              <p className="text-lg font-semibold text-text-primary">
                {yieldSummary ? formatPercent(yieldSummary.avg_yield) : '—'}
              </p>
              <p className="text-xs text-text-muted mt-1">
                Max {yieldSummary ? formatPercent(yieldSummary.max_yield) : '—'} • Min {yieldSummary ? formatPercent(yieldSummary.min_yield) : '—'}
              </p>
            </div>
            <div className="p-3 bg-background-secondary rounded-lg">
              <PieChart
                data={[
                  { name: 'Réel', value: yieldSummary?.zones_with_real_data || 0 },
                  { name: 'Estimé', value: yieldSummary?.zones_with_estimated_data || 0 }
                ]}
                height={180}
                innerRadius={50}
                outerRadius={70}
                showLabels={false}
                centerLabel={yieldSummary?.total_zones || 0}
                colors={['#10B981', '#3B82F6']}
              />
            </div>
          </div>
        </Card>
      </div>

      {/* Alerts Banner */}
      <AlertsBanner />

      {/* Opportunities + Regimes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardTitle>Top Opportunities</CardTitle>
          <CardSubtitle>Résumé des meilleurs deals</CardSubtitle>
          <div className="table-container mt-4">
            <table className="table">
              <thead>
                <tr>
                  <th>Location</th>
                  <th>Score</th>
                  <th>Discount</th>
                  <th>Strategy</th>
                </tr>
              </thead>
              <tbody>
                {top_opportunities.slice(0, 6).map((opp) => (
                  <tr key={opp.id}>
                    <td>
                      <div className="font-medium text-text-primary">{opp.community}</div>
                      <div className="text-xs text-text-muted">{opp.building || ''}</div>
                    </td>
                    <td>{Math.round(opp.global_score)}</td>
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

        <Card>
          <CardTitle>Market Regimes</CardTitle>
          <CardSubtitle>Signaux de tendance</CardSubtitle>
          <div className="space-y-2 mt-4">
            {regimes.slice(0, 6).map((r, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-background-secondary rounded-lg"
              >
                <span className="text-sm text-text-primary truncate max-w-[160px]">
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
      </div>

      {/* Transactions Table */}
      <Card>
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <CardTitle>Transactions</CardTitle>
            <CardSubtitle>Liste unique avec filtre période</CardSubtitle>
          </div>
          <Select
            value={txDays}
            onChange={setTxDays}
            options={txOptions}
            className="w-32"
          />
        </div>
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
              {transactions.map((tx, index) => (
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
      </div>
    </div>
  )
}
