'use client'

import { useEffect, useState } from 'react'
import { Card, CardTitle, CardSubtitle } from '@/components/ui/Card'
import { AlertsBanner } from '@/components/ui/AlertsBanner'
import { KpiCard, KpiGrid } from '@/components/ui/KpiCard'
import { LoadingPage } from '@/components/ui/Loading'
import { Select } from '@/components/ui/Select'
import { AreaChart, BarChart } from '@/components/charts'
import { formatCompact, formatPercent } from '@/lib/utils'
import { TrendingUp, TrendingDown, Activity, BarChart3 } from 'lucide-react'
import { useAutoRefresh } from '@/lib/useAutoRefresh'

export default function InsightsPage() {
  const AUTO_REFRESH_MS = 5000
  const [loading, setLoading] = useState(true)
  const [periodDays, setPeriodDays] = useState('30')
  const [marketData, setMarketData] = useState<{
    historical: Array<{ week: string; avg_price: number; volume: number }>
    zones: Array<{ community: string; avg_price_sqft: number; transaction_count: number; volatility?: number }>
  } | null>(null)
  const [question, setQuestion] = useState('')
  const [aiMessages, setAiMessages] = useState<Array<{ role: 'user' | 'assistant'; text: string }>>([])

  useEffect(() => {
    fetchMarketData()
  }, [])

  const fetchMarketData = async () => {
    try {
      setLoading(true)
      const days = parseInt(periodDays, 10)
      
      // Fetch historical data
      const [histRes, zonesRes] = await Promise.all([
        fetch('/api/transactions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'get_historical', days: Number.isFinite(days) ? days : 30 })
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

  useAutoRefresh({
    intervalMs: AUTO_REFRESH_MS,
    onTick: fetchMarketData,
    deps: [periodDays]
  })

  if (loading && !marketData) return <LoadingPage />
  if (!marketData) return <div className="text-text-muted p-4">No data available</div>

  const { historical, zones } = marketData

  // Calculate insights
  const totalVolume = historical.reduce((sum, h) => sum + h.volume, 0)
  const avgPrice = historical.length > 0 
    ? historical.reduce((sum, h) => sum + h.avg_price, 0) / historical.length 
    : 0
  
  const periodLabel = periodDays === '30' ? '1 month' : periodDays === '90' ? '3 months' : '6 months'
  const hasTrendWindow = historical.length >= 8
  const recentSlice = hasTrendWindow ? historical.slice(-4) : []
  const olderSlice = hasTrendWindow ? historical.slice(0, 4) : []
  const recentPrice = recentSlice.length ? recentSlice.reduce((sum, h) => sum + h.avg_price, 0) / recentSlice.length : 0
  const olderPrice = olderSlice.length ? olderSlice.reduce((sum, h) => sum + h.avg_price, 0) / olderSlice.length : 0
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

  // Market regime based on RSI
  const getMarketRegime = (rsiValue: number) => {
    if (rsiValue >= 70) return { label: 'Overbought', color: '#EF4444' }
    if (rsiValue <= 30) return { label: 'Oversold', color: '#10B981' }
    if (rsiValue >= 50) return { label: 'Bullish', color: '#3B82F6' }
    return { label: 'Bearish', color: '#F59E0B' }
  }

  const regime = getMarketRegime(rsi)

  const zoneSignals = zones.map(zone => {
    const volatility = typeof zone.volatility === 'number' ? zone.volatility : 0
    const isBuy = volatility <= 0.15 && zone.transaction_count >= 8
    const isAvoid = volatility >= 0.25
    return {
      ...zone,
      signal: isBuy ? 'BUY' : isAvoid ? 'AVOID' : 'WATCH',
      volatility
    }
  })

  const buyZones = zoneSignals.filter(z => z.signal === 'BUY').slice(0, 3)
  const watchZones = zoneSignals.filter(z => z.signal === 'WATCH').slice(0, 3)
  const avoidZones = zoneSignals.filter(z => z.signal === 'AVOID').slice(0, 3)

  const forecastText = priceTrend > 5
    ? 'Momentum positif. Prioriser les zones stables avec volume élevé.'
    : priceTrend < -3
      ? 'Correction en cours. Se concentrer sur la qualité et le long terme.'
      : 'Marché neutre. Favoriser des stratégies rendement.'

  const handleAsk = () => {
    const trimmed = question.trim()
    if (!trimmed) return
    setAiMessages(prev => ([
      ...prev,
      { role: 'user', text: trimmed },
      { role: 'assistant', text: 'Assistant IA non configuré. Connectez un endpoint pour activer les réponses.' }
    ]))
    setQuestion('')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Market Insights</h1>
          <p className="text-text-muted text-sm mt-1">AI-powered market intelligence and predictions</p>
        </div>
        <div className="flex items-center gap-3">
          <Select
            value={periodDays}
            onChange={setPeriodDays}
            options={[
              { value: '30', label: 'Month (30d)' },
              { value: '90', label: 'Quarter (90d)' },
              { value: '180', label: '6 Months (180d)' }
            ]}
            className="w-44"
          />
        </div>
      </div>

      {/* Key Metrics */}
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
          title="Price Trend"
          subtitle={`${periodLabel} change`}
          value={formatPercent(priceTrend, true)}
          trend={priceTrend}
          color={priceTrend > 0 ? 'success' : 'danger'}
          showLive
        />
        <KpiCard
          title="Total Volume"
          subtitle="Transactions"
          value={formatCompact(totalVolume)}
          icon={<BarChart3 className="w-5 h-5" />}
          showLive
        />
        <KpiCard
          title="Market Regime"
          subtitle="Current state"
          value={regime.label}
          color={regime.label === 'Bullish' ? 'success' : regime.label === 'Overbought' ? 'danger' : 'warning'}
          showLive
        />
      </KpiGrid>

      <AlertsBanner />

      {/* Market Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardTitle>Évolution des prix</CardTitle>
          <CardSubtitle>Prix moyen par semaine ({periodLabel})</CardSubtitle>
          <AreaChart
            data={priceChartData}
            dataKey="price"
            xAxisKey="name"
            height={260}
            color="#10B981"
          />
        </Card>

        <Card>
          <CardTitle>Volume de transactions</CardTitle>
          <CardSubtitle>Nombre de transactions ({periodLabel})</CardSubtitle>
          <BarChart
            data={volumeChartData}
            dataKey="volume"
            xAxisKey="name"
            height={260}
            color="#3B82F6"
          />
        </Card>
      </div>

      {/* Recap */}
      <div className="section-title">Recap IA (actionnable)</div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card accent accentColor="#10B981">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-5 h-5 text-success" />
            <span className="font-semibold text-text-primary">À acheter</span>
          </div>
          <div className="text-sm text-text-secondary space-y-1">
            {buyZones.length ? buyZones.map(zone => (
              <div key={zone.community}>{zone.community}</div>
            )) : <div>Aucun signal fort</div>}
          </div>
        </Card>

        <Card accent accentColor="#F59E0B">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-5 h-5 text-warning" />
            <span className="font-semibold text-text-primary">À surveiller</span>
          </div>
          <div className="text-sm text-text-secondary space-y-1">
            {watchZones.length ? watchZones.map(zone => (
              <div key={zone.community}>{zone.community}</div>
            )) : <div>Pas de zone stable</div>}
          </div>
        </Card>

        <Card accent accentColor="#EF4444">
          <div className="flex items-center gap-2 mb-2">
            <TrendingDown className="w-5 h-5 text-danger" />
            <span className="font-semibold text-text-primary">À éviter</span>
          </div>
          <div className="text-sm text-text-secondary space-y-1">
            {avoidZones.length ? avoidZones.map(zone => (
              <div key={zone.community}>{zone.community}</div>
            )) : <div>Aucun signal rouge</div>}
          </div>
        </Card>
      </div>

      <Card>
        <CardTitle>Prévision synthétique</CardTitle>
        <CardSubtitle>Lecture rapide du momentum</CardSubtitle>
        <div className="mt-3 text-sm text-text-secondary">
          {forecastText}
        </div>
      </Card>

      {/* AI Q&A */}
      <Card>
        <CardTitle>Question IA</CardTitle>
        <CardSubtitle>Posez vos questions sur le marché</CardSubtitle>
        <div className="mt-4 space-y-3">
          <div className="flex items-center gap-3">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ex: Où investir ce mois-ci ?"
              className="input flex-1"
            />
            <button onClick={handleAsk} className="btn-secondary">Envoyer</button>
          </div>
          {aiMessages.length > 0 && (
            <div className="space-y-2">
              {aiMessages.map((msg, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg text-sm ${msg.role === 'user' ? 'bg-background-secondary text-text-primary' : 'bg-accent/10 text-text-secondary'}`}
                >
                  {msg.text}
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}
