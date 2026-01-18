'use client'

import { useEffect, useState } from 'react'
import { Card, CardTitle, CardSubtitle } from '@/components/ui/Card'
import { KpiCard, KpiGrid } from '@/components/ui/KpiCard'
import { LoadingPage } from '@/components/ui/Loading'
import { AreaChart, BarChart, LineChart } from '@/components/charts'
import { formatCompact, formatPercent } from '@/lib/utils'
import { TrendingUp, TrendingDown, Activity, BarChart3 } from 'lucide-react'

export default function InsightsPage() {
  const [loading, setLoading] = useState(true)
  const [marketData, setMarketData] = useState<{
    historical: Array<{ week: string; avg_price: number; volume: number }>
    zones: Array<{ community: string; avg_price_sqft: number; transaction_count: number }>
  } | null>(null)

  useEffect(() => {
    fetchMarketData()
  }, [])

  const fetchMarketData = async () => {
    try {
      setLoading(true)
      
      // Fetch historical data
      const [histRes, zonesRes] = await Promise.all([
        fetch('/api/transactions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'get_historical', days: 180 })
        }),
        fetch('/api/zones')
      ])
      
      const histJson = await histRes.json()
      const zonesJson = await zonesRes.json()
      
      setMarketData({
        historical: histJson.historical || [],
        zones: zonesJson.zones || []
      })
    } catch (err) {
      console.error('Failed to fetch market data:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <LoadingPage />
  if (!marketData) return <div className="text-text-muted p-4">No data available</div>

  const { historical, zones } = marketData

  // Calculate insights
  const totalVolume = historical.reduce((sum, h) => sum + h.volume, 0)
  const avgPrice = historical.length > 0 
    ? historical.reduce((sum, h) => sum + h.avg_price, 0) / historical.length 
    : 0
  
  const recentPrice = historical.slice(-4).reduce((sum, h) => sum + h.avg_price, 0) / 4
  const olderPrice = historical.slice(0, 4).reduce((sum, h) => sum + h.avg_price, 0) / 4
  const priceTrend = olderPrice > 0 ? ((recentPrice - olderPrice) / olderPrice) * 100 : 0

  // Calculate market RSI (simplified)
  const calculateRSI = () => {
    if (historical.length < 14) return 50
    const prices = historical.map(h => h.avg_price)
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

  // Chart data
  const priceChartData = historical.map(h => ({
    name: h.week.slice(5),
    price: h.avg_price
  }))

  const volumeChartData = historical.map(h => ({
    name: h.week.slice(5),
    volume: h.volume
  }))

  const zoneChartData = zones.slice(0, 10).map(z => ({
    name: z.community.slice(0, 12),
    price: z.avg_price_sqft,
    volume: z.transaction_count
  }))

  // Market regime based on RSI
  const getMarketRegime = (rsiValue: number) => {
    if (rsiValue >= 70) return { label: 'Overbought', color: '#EF4444' }
    if (rsiValue <= 30) return { label: 'Oversold', color: '#10B981' }
    if (rsiValue >= 50) return { label: 'Bullish', color: '#3B82F6' }
    return { label: 'Bearish', color: '#F59E0B' }
  }

  const regime = getMarketRegime(rsi)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Market Insights</h1>
        <p className="text-text-muted text-sm mt-1">AI-powered market intelligence and predictions</p>
      </div>

      {/* Key Metrics */}
      <KpiGrid className="grid-cols-2 md:grid-cols-4">
        <KpiCard
          title="Market RSI"
          subtitle="Momentum indicator"
          value={Math.round(rsi)}
          color={rsi > 70 ? 'danger' : rsi < 30 ? 'success' : 'info'}
          icon={<Activity className="w-5 h-5" />}
        />
        <KpiCard
          title="Price Trend"
          subtitle="6 month change"
          value={formatPercent(priceTrend, true)}
          trend={priceTrend}
          color={priceTrend > 0 ? 'success' : 'danger'}
        />
        <KpiCard
          title="Total Volume"
          subtitle="Transactions"
          value={formatCompact(totalVolume)}
          icon={<BarChart3 className="w-5 h-5" />}
        />
        <KpiCard
          title="Market Regime"
          subtitle="Current state"
          value={regime.label}
          color={regime.label === 'Bullish' ? 'success' : regime.label === 'Overbought' ? 'danger' : 'warning'}
        />
      </KpiGrid>

      {/* Price Evolution */}
      <Card>
        <CardTitle>Price Evolution</CardTitle>
        <CardSubtitle>Average price per sqft over time</CardSubtitle>
        <AreaChart
          data={priceChartData}
          dataKey="price"
          xAxisKey="name"
          height={300}
          color="#00D9A3"
        />
      </Card>

      {/* Volume Trend */}
      <Card>
        <CardTitle>Transaction Volume</CardTitle>
        <CardSubtitle>Weekly transaction count</CardSubtitle>
        <BarChart
          data={volumeChartData}
          dataKey="volume"
          xAxisKey="name"
          height={250}
          color="#3B82F6"
        />
      </Card>

      {/* AI Insights */}
      <div className="section-title">AI Market Insights</div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card accent accentColor={priceTrend > 0 ? '#10B981' : '#EF4444'}>
          <div className="flex items-center gap-2 mb-2">
            {priceTrend > 0 ? <TrendingUp className="w-5 h-5 text-success" /> : <TrendingDown className="w-5 h-5 text-danger" />}
            <span className="font-semibold text-text-primary">
              {priceTrend > 5 ? 'Strong Market' : priceTrend > 0 ? 'Steady Growth' : 'Market Correction'}
            </span>
          </div>
          <p className="text-sm text-text-secondary">
            {priceTrend > 0 
              ? `Prices up ${formatPercent(priceTrend)} over 6 months. Consider accumulating in undervalued zones.`
              : `Market showing correction of ${formatPercent(Math.abs(priceTrend))}. Look for value opportunities.`
            }
          </p>
        </Card>

        <Card accent accentColor={rsi > 50 ? '#3B82F6' : '#F59E0B'}>
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-5 h-5" style={{ color: regime.color }} />
            <span className="font-semibold text-text-primary">Momentum: {regime.label}</span>
          </div>
          <p className="text-sm text-text-secondary">
            RSI at {Math.round(rsi)} indicates {rsi > 70 ? 'overbought conditions - exercise caution' : rsi < 30 ? 'oversold conditions - potential buying opportunity' : 'neutral momentum - stable market'}.
          </p>
        </Card>

        <Card accent accentColor="#8B5CF6">
          <div className="flex items-center gap-2 mb-2">
            <BarChart3 className="w-5 h-5 text-purple" />
            <span className="font-semibold text-text-primary">Volume Analysis</span>
          </div>
          <p className="text-sm text-text-secondary">
            {totalVolume > 1000 
              ? 'High liquidity market with strong transaction volume. Good for FLIP strategies.'
              : 'Moderate transaction volume. Focus on quality over quantity.'}
          </p>
        </Card>

        <Card accent accentColor="#00D9A3">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-5 h-5 text-accent" />
            <span className="font-semibold text-text-primary">Strategy Recommendation</span>
          </div>
          <p className="text-sm text-text-secondary">
            {priceTrend > 5 && rsi < 70 
              ? 'FLIP strategy recommended - strong momentum with room to grow.'
              : priceTrend < 0 
              ? 'LONG_TERM strategy - accumulate during correction for future gains.'
              : 'RENT strategy - stable market suits income-focused approach.'}
          </p>
        </Card>
      </div>

      {/* Zone Comparison */}
      <Card>
        <CardTitle>Zone Performance Comparison</CardTitle>
        <CardSubtitle>Top 10 zones by average price</CardSubtitle>
        <LineChart
          data={zoneChartData}
          lines={[
            { dataKey: 'price', color: '#10B981', name: 'Avg Price' },
            { dataKey: 'volume', color: '#3B82F6', name: 'Volume', strokeDasharray: '5 5' }
          ]}
          xAxisKey="name"
          height={300}
          showLegend
        />
      </Card>
    </div>
  )
}
