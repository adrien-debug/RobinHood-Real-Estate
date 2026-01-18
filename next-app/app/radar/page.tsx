'use client'

import { useEffect, useState } from 'react'
import { KpiCard, KpiGrid } from '@/components/ui/KpiCard'
import { Card, CardTitle, CardSubtitle } from '@/components/ui/Card'
import { Select } from '@/components/ui/Select'
import { DatePicker } from '@/components/ui/DatePicker'
import { LoadingPage } from '@/components/ui/Loading'
import { Badge, StrategyBadge, RegimeBadge } from '@/components/ui/Badge'
import { PieChart, ScatterChart, BarChart } from '@/components/charts'
import { formatPercent, formatDateAPI, getStrategyColor } from '@/lib/utils'
import { Target, TrendingUp, AlertTriangle, Zap } from 'lucide-react'
import type { Opportunity } from '@/lib/types/database'

interface OpportunitiesData {
  opportunities: Opportunity[]
  stats: {
    total: number
    by_strategy: Record<string, number>
    avg_discount: number
    avg_score: number
  }
}

export default function RadarPage() {
  const [data, setData] = useState<OpportunitiesData | null>(null)
  const [loading, setLoading] = useState(true)
  
  const [selectedDate, setSelectedDate] = useState(formatDateAPI(new Date()))
  const [strategy, setStrategy] = useState('All')
  const [minScore, setMinScore] = useState(50)
  const [regime, setRegime] = useState('All')

  useEffect(() => {
    fetchOpportunities()
  }, [selectedDate, strategy, minScore, regime])

  const fetchOpportunities = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({
        date: selectedDate,
        min_score: minScore.toString()
      })
      if (strategy !== 'All') params.append('strategy', strategy)
      if (regime !== 'All') params.append('regime', regime)
      
      const res = await fetch(`/api/opportunities?${params}`)
      const json = await res.json()
      setData(json)
    } catch (err) {
      console.error('Failed to fetch opportunities:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading && !data) return <LoadingPage />
  if (!data) return null

  const { opportunities, stats } = data

  // Chart data
  const strategyChartData = Object.entries(stats.by_strategy).map(([name, value]) => ({
    name,
    value
  }))

  const scoreDistribution = [
    { name: '50-60', value: opportunities.filter(o => (o.global_score || 0) >= 50 && (o.global_score || 0) < 60).length },
    { name: '60-70', value: opportunities.filter(o => (o.global_score || 0) >= 60 && (o.global_score || 0) < 70).length },
    { name: '70-80', value: opportunities.filter(o => (o.global_score || 0) >= 70 && (o.global_score || 0) < 80).length },
    { name: '80-90', value: opportunities.filter(o => (o.global_score || 0) >= 80 && (o.global_score || 0) < 90).length },
    { name: '90+', value: opportunities.filter(o => (o.global_score || 0) >= 90).length },
  ]

  const scatterData = opportunities.map(o => ({
    discount: o.discount_pct || 0,
    score: o.global_score || 0,
    name: o.community || 'N/A'
  }))

  // Top signals
  const topOpps = opportunities.slice(0, 5)

  const getSignalType = (score: number, discount: number) => {
    if (score >= 85 || discount >= 20) return { type: 'BUY', color: '#10B981' }
    if (score >= 70 || discount >= 10) return { type: 'HOLD', color: '#F59E0B' }
    return { type: 'WAIT', color: '#6B7280' }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Investment Radar</h1>
          <p className="text-text-muted text-sm mt-1">Opportunities ranked by score</p>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          <DatePicker 
            value={selectedDate}
            onChange={setSelectedDate}
            max={formatDateAPI(new Date())}
            className="w-40"
          />
          <Select
            value={strategy}
            onChange={setStrategy}
            options={[
              { value: 'All', label: 'All Strategies' },
              { value: 'FLIP', label: 'FLIP' },
              { value: 'RENT', label: 'RENT' },
              { value: 'LONG', label: 'LONG' },
            ]}
            className="w-36"
          />
          <Select
            value={regime}
            onChange={setRegime}
            options={[
              { value: 'All', label: 'All Regimes' },
              { value: 'ACCUMULATION', label: 'Accumulation' },
              { value: 'EXPANSION', label: 'Expansion' },
              { value: 'DISTRIBUTION', label: 'Distribution' },
              { value: 'RETOURNEMENT', label: 'Retournement' },
            ]}
            className="w-40"
          />
          <div className="flex items-center gap-2 bg-background-secondary rounded-lg px-3 py-2">
            <span className="text-xs text-text-muted">Min Score:</span>
            <input
              type="range"
              min="0"
              max="100"
              value={minScore}
              onChange={(e) => setMinScore(parseInt(e.target.value))}
              className="w-24"
            />
            <span className="text-sm text-text-primary w-8">{minScore}</span>
          </div>
        </div>
      </div>

      {/* KPIs */}
      <KpiGrid className="grid-cols-2 md:grid-cols-5">
        <KpiCard
          title="Total"
          subtitle="Opportunities"
          value={stats.total}
          icon={<Target className="w-5 h-5" />}
          color="accent"
        />
        <KpiCard
          title="FLIP"
          subtitle="Strategy"
          value={stats.by_strategy.FLIP || 0}
          color="success"
        />
        <KpiCard
          title="RENT"
          subtitle="Strategy"
          value={stats.by_strategy.RENT || 0}
          color="info"
        />
        <KpiCard
          title="Avg Score"
          subtitle="Quality"
          value={`${Math.round(stats.avg_score)}%`}
          color="success"
        />
        <KpiCard
          title="Avg Discount"
          subtitle="Below market"
          value={formatPercent(stats.avg_discount)}
        />
      </KpiGrid>

      {/* Trading Signals */}
      <div className="section-title">Trading Signals</div>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {topOpps.map((opp, index) => {
          const signal = getSignalType(opp.global_score || 0, opp.discount_pct || 0)
          return (
            <Card 
              key={index}
              accent
              accentColor={signal.color}
              className="min-h-[160px] flex flex-col"
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="font-bold" style={{ color: signal.color }}>{signal.type}</span>
                <Badge variant={signal.type === 'BUY' ? 'success' : signal.type === 'HOLD' ? 'warning' : 'default'}>
                  {((opp.global_score || 0) / 20).toFixed(1)}
                </Badge>
              </div>
              <p className="text-xs text-text-muted truncate">{opp.community?.slice(0, 15)}...</p>
              <div className="flex-1 mt-2">
                <p className="text-sm text-text-secondary">Score: {Math.round(opp.global_score || 0)}</p>
                <p className="text-sm text-text-secondary">Discount: {(opp.discount_pct || 0).toFixed(1)}%</p>
              </div>
              <div className="mt-2 pt-2 border-t border-border">
                <span className="text-xs font-semibold" style={{ color: signal.color }}>→ EXECUTE</span>
              </div>
            </Card>
          )
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Strategy Distribution */}
        <Card>
          <CardTitle>Strategy Distribution</CardTitle>
          <PieChart
            data={strategyChartData}
            height={300}
            centerLabel={stats.total}
            colors={['#10B981', '#3B82F6', '#F59E0B', '#6B7280']}
          />
        </Card>

        {/* Score vs Discount */}
        <Card>
          <CardTitle>Score vs Discount</CardTitle>
          <CardSubtitle>Opportunity mapping</CardSubtitle>
          <ScatterChart
            data={scatterData}
            xKey="discount"
            yKey="score"
            xLabel="Discount %"
            yLabel="Score"
            height={300}
          />
        </Card>
      </div>

      {/* Score Distribution */}
      <Card>
        <CardTitle>Score Distribution</CardTitle>
        <BarChart
          data={scoreDistribution}
          dataKey="value"
          xAxisKey="name"
          height={200}
          colors={['#F59E0B', '#F59E0B', '#3B82F6', '#10B981', '#10B981']}
        />
      </Card>

      {/* Opportunities Table */}
      <Card>
        <CardTitle>All Opportunities</CardTitle>
        <CardSubtitle>Sorted by score</CardSubtitle>
        <div className="table-container mt-4">
          <table className="table">
            <thead>
              <tr>
                <th>Location</th>
                <th>Type</th>
                <th>Score</th>
                <th>Discount</th>
                <th>Strategy</th>
                <th>Regime</th>
              </tr>
            </thead>
            <tbody>
              {opportunities.map((opp, index) => (
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
                          className="progress-bar" 
                          style={{ 
                            width: `${opp.global_score}%`,
                            backgroundColor: (opp.global_score || 0) >= 80 ? '#10B981' : (opp.global_score || 0) >= 60 ? '#3B82F6' : '#F59E0B'
                          }}
                        />
                      </div>
                      <span className="text-sm font-medium">{Math.round(opp.global_score || 0)}</span>
                    </div>
                  </td>
                  <td className="text-success font-medium">-{(opp.discount_pct || 0).toFixed(1)}%</td>
                  <td>
                    <StrategyBadge strategy={opp.recommended_strategy || 'IGNORE'} />
                  </td>
                  <td>
                    {opp.market_regime && <RegimeBadge regime={opp.market_regime} />}
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
