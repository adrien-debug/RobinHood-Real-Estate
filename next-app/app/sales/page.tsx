'use client'

import { useEffect, useState } from 'react'
import { KpiCard, KpiGrid } from '@/components/ui/KpiCard'
import { Card, CardTitle, CardSubtitle } from '@/components/ui/Card'
import { Select } from '@/components/ui/Select'
import { DatePicker } from '@/components/ui/DatePicker'
import { LoadingPage } from '@/components/ui/Loading'
import { BarChart, AreaChart, ScatterChart, LineChart } from '@/components/charts'
import { formatCurrency, formatCompact, formatPercent, formatDateAPI } from '@/lib/utils'
import type { Transaction } from '@/lib/types/database'
import { useAutoRefresh } from '@/lib/useAutoRefresh'

interface TransactionsData {
  transactions: Transaction[]
  total: number
  stats: {
    total_volume: number
    avg_price_sqft: number
    below_market_count: number
    below_market_pct: number
  }
}

interface HistoricalData {
  week: string
  avg_price: number
  volume: number
}

export default function SalesPage() {
  const AUTO_REFRESH_MS = 5000
  const [data, setData] = useState<TransactionsData | null>(null)
  const [historical, setHistorical] = useState<HistoricalData[]>([])
  const [communities, setCommunities] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Filters
  const [selectedDate, setSelectedDate] = useState(formatDateAPI(new Date()))
  const [selectedCommunity, setSelectedCommunity] = useState('All')
  const [selectedRooms, setSelectedRooms] = useState('All')
  const [minPrice, setMinPrice] = useState('')

  useEffect(() => {
    fetchCommunities()
    fetchHistorical()
  }, [])

  useEffect(() => {
    fetchTransactions()
  }, [selectedDate, selectedCommunity, selectedRooms, minPrice])

  const fetchCommunities = async () => {
    try {
      const res = await fetch('/api/transactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'get_communities' })
      })
      const json = await res.json()
      setCommunities(json.communities || [])
    } catch (err) {
      console.error('Failed to fetch communities:', err)
    }
  }

  const fetchHistorical = async () => {
    try {
      const res = await fetch('/api/transactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'get_historical', days: 90 })
      })
      const json = await res.json()
      setHistorical(json.historical || [])
    } catch (err) {
      console.error('Failed to fetch historical:', err)
    }
  }

  const fetchTransactions = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({ date: selectedDate })
      if (selectedCommunity !== 'All') params.append('community', selectedCommunity)
      if (selectedRooms !== 'All') params.append('rooms', selectedRooms)
      if (minPrice) params.append('min_price', minPrice)
      
      const res = await fetch(`/api/transactions?${params}`)
      if (!res.ok) throw new Error('Failed to fetch')
      const json = await res.json()
      setData(json)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  useAutoRefresh({
    intervalMs: AUTO_REFRESH_MS,
    onTick: () => {
      fetchTransactions()
      fetchHistorical()
    },
    deps: [selectedDate, selectedCommunity, selectedRooms, minPrice]
  })

  if (loading && !data) return <LoadingPage />
  if (error) return <div className="text-danger p-4">{error}</div>
  if (!data) return null

  const { transactions, stats } = data

  // Prepare chart data
  const priceDistribution = transactions
    .filter(t => t.price_per_sqft)
    .reduce((acc, t) => {
      const bucket = Math.floor((t.price_per_sqft || 0) / 500) * 500
      const key = `${bucket}-${bucket + 500}`
      acc[key] = (acc[key] || 0) + 1
      return acc
    }, {} as Record<string, number>)

  const priceDistData = Object.entries(priceDistribution)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => parseInt(a.name) - parseInt(b.name))

  const roomsDistribution = transactions.reduce((acc, t) => {
    const room = t.rooms_bucket || 'Unknown'
    acc[room] = (acc[room] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const roomsData = Object.entries(roomsDistribution).map(([name, value]) => ({ name, value }))

  const scatterData = transactions
    .filter(t => t.area_sqft && t.price_per_sqft)
    .map(t => ({
      area: t.area_sqft,
      price: t.price_per_sqft,
      name: t.community
    }))

  const historicalChartData = historical.map(h => ({
    name: h.week.slice(5), // MM-DD format
    price: h.avg_price,
    volume: h.volume
  }))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Sales Analytics</h1>
          <p className="text-text-muted text-sm mt-1">Transaction analysis and market trends</p>
        </div>
        
        <div className="flex items-center gap-3 flex-wrap">
          <DatePicker 
            value={selectedDate}
            onChange={setSelectedDate}
            max={formatDateAPI(new Date())}
            className="w-40"
          />
          <Select
            value={selectedCommunity}
            onChange={setSelectedCommunity}
            options={[{ value: 'All', label: 'All Communities' }, ...communities.map(c => ({ value: c, label: c }))]}
            className="w-48"
          />
          <Select
            value={selectedRooms}
            onChange={setSelectedRooms}
            options={[
              { value: 'All', label: 'All Types' },
              { value: 'studio', label: 'Studio' },
              { value: '1BR', label: '1BR' },
              { value: '2BR', label: '2BR' },
              { value: '3BR+', label: '3BR+' },
            ]}
            className="w-32"
          />
        </div>
      </div>

      {/* KPIs */}
      <KpiGrid className="grid-cols-2 md:grid-cols-4">
        <KpiCard
          title="Transactions"
          subtitle="Today"
          value={transactions.length}
          color="accent"
        />
        <KpiCard
          title="Total Volume"
          subtitle="AED"
          value={formatCompact(stats.total_volume)}
        />
        <KpiCard
          title="Avg Price/sqft"
          subtitle="AED"
          value={Math.round(stats.avg_price_sqft).toLocaleString()}
        />
        <KpiCard
          title="Below Market"
          subtitle="Opportunities"
          value={formatPercent(stats.below_market_pct)}
          color="success"
        />
      </KpiGrid>

      {/* Historical Trends */}
      <Card>
        <CardTitle>Price & Volume Trends</CardTitle>
        <CardSubtitle>Last 90 days weekly data</CardSubtitle>
        <LineChart
          data={historicalChartData}
          lines={[
            { dataKey: 'price', color: '#10B981', name: 'Avg Price' },
            { dataKey: 'volume', color: '#3B82F6', name: 'Volume', strokeDasharray: '5 5' }
          ]}
          xAxisKey="name"
          height={300}
          showLegend
        />
      </Card>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Price Distribution */}
        <Card>
          <CardTitle>Price Distribution</CardTitle>
          <CardSubtitle>AED per sqft ranges</CardSubtitle>
          <BarChart
            data={priceDistData}
            dataKey="value"
            xAxisKey="name"
            color="#10B981"
            height={280}
          />
        </Card>

        {/* By Room Type */}
        <Card>
          <CardTitle>By Room Type</CardTitle>
          <CardSubtitle>Transaction count</CardSubtitle>
          <BarChart
            data={roomsData}
            dataKey="value"
            xAxisKey="name"
            height={280}
            colors={['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#6B7280']}
          />
        </Card>
      </div>

      {/* Price vs Size Scatter */}
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

      {/* Transactions Table */}
      <Card>
        <CardTitle>Transactions</CardTitle>
        <CardSubtitle>Latest sales</CardSubtitle>
        <div className="table-container mt-4">
          <table className="table">
            <thead>
              <tr>
                <th>Location</th>
                <th>Type</th>
                <th>Area</th>
                <th>Price</th>
                <th>AED/sqft</th>
                <th>vs Market</th>
              </tr>
            </thead>
            <tbody>
              {transactions.slice(0, 20).map((tx, index) => {
                const discount = tx.price_per_sqft && stats.avg_price_sqft 
                  ? ((stats.avg_price_sqft - tx.price_per_sqft) / stats.avg_price_sqft) * 100
                  : 0
                return (
                  <tr key={index}>
                    <td>
                      <div className="font-medium text-text-primary">{tx.community || 'N/A'}</div>
                      <div className="text-xs text-text-muted">{tx.building || ''}</div>
                    </td>
                    <td>{tx.rooms_bucket || 'N/A'}</td>
                    <td>{tx.area_sqft ? `${Math.round(tx.area_sqft)} sqft` : 'N/A'}</td>
                    <td>{formatCurrency(tx.price_aed || 0)}</td>
                    <td>{tx.price_per_sqft ? Math.round(tx.price_per_sqft).toLocaleString() : 'N/A'}</td>
                    <td className={discount > 0 ? 'text-success' : discount < 0 ? 'text-danger' : ''}>
                      {discount !== 0 ? `${discount > 0 ? '-' : '+'}${Math.abs(discount).toFixed(1)}%` : 'At market'}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
