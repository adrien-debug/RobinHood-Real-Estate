import { NextRequest, NextResponse } from 'next/server'
import { getServerClient } from '@/lib/supabase'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const date = searchParams.get('date') || new Date().toISOString().split('T')[0]
    const community = searchParams.get('community')
    
    const supabase = getServerClient()
    
    if (community) {
      // Get specific zone data
      const [baselines, regime, priceHistory] = await Promise.all([
        // Market baselines for community
        supabase
          .from('dld_market_baselines')
          .select('*')
          .eq('community', community)
          .order('transaction_count', { ascending: false }),
        
        // Market regime
        supabase
          .from('dld_market_regimes')
          .select('*')
          .eq('community', community)
          .limit(1)
          .single(),
        
        // Price history (30 days)
        supabase
          .from('dld_transactions')
          .select('transaction_date, price_per_sqft')
          .eq('community', community)
          .gte('transaction_date', getDateMinusDays(date, 30))
          .not('price_per_sqft', 'is', null)
          .order('transaction_date')
      ])
      
      // Group price history by day
      const dailyPrices = groupByDay(priceHistory.data || [])
      
      return NextResponse.json({
        community,
        baselines: baselines.data || [],
        regime: regime.data,
        price_history: dailyPrices
      })
      
    } else {
      // Get zone comparison data
      const { data, error } = await supabase
        .from('dld_transactions')
        .select('community, price_per_sqft')
        .gte('transaction_date', getDateMinusDays(date, 90))
        .not('community', 'is', null)
        .not('price_per_sqft', 'is', null)
      
      if (error) throw error
      
      // Aggregate by community
      const zoneStats = aggregateByZone(data || [])
      
      // Get communities with most transactions
      const topZones = zoneStats
        .filter(z => z.transaction_count >= 5)
        .sort((a, b) => b.avg_price_sqft - a.avg_price_sqft)
        .slice(0, 15)
      
      // Get communities list
      const communities = zoneStats
        .filter(z => z.transaction_count >= 3)
        .map(z => z.community)
        .sort()
      
      return NextResponse.json({
        zones: topZones,
        communities
      })
    }
    
  } catch (error) {
    console.error('Zones API error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch zone data' },
      { status: 500 }
    )
  }
}

function getDateMinusDays(date: string, days: number): string {
  const d = new Date(date)
  d.setDate(d.getDate() - days)
  return d.toISOString().split('T')[0]
}

function groupByDay(data: Array<{ transaction_date: string; price_per_sqft: number | null }>) {
  const days: Record<string, number[]> = {}
  
  for (const item of data) {
    const day = item.transaction_date
    if (!days[day]) days[day] = []
    if (item.price_per_sqft) days[day].push(item.price_per_sqft)
  }
  
  return Object.entries(days).map(([date, prices]) => ({
    date,
    avg_price: prices.length > 0 ? prices.reduce((a, b) => a + b, 0) / prices.length : 0,
    count: prices.length
  })).sort((a, b) => a.date.localeCompare(b.date))
}

function aggregateByZone(data: Array<{ community: string | null; price_per_sqft: number | null }>) {
  const zones: Record<string, { prices: number[] }> = {}
  
  for (const item of data) {
    if (!item.community || !item.price_per_sqft) continue
    
    if (!zones[item.community]) {
      zones[item.community] = { prices: [] }
    }
    zones[item.community].prices.push(item.price_per_sqft)
  }
  
  return Object.entries(zones).map(([community, data]) => ({
    community,
    avg_price_sqft: data.prices.length > 0 ? data.prices.reduce((a, b) => a + b, 0) / data.prices.length : 0,
    transaction_count: data.prices.length,
    volatility: calculateVolatility(data.prices)
  }))
}

function calculateVolatility(prices: number[]): number {
  if (prices.length < 2) return 0
  const avg = prices.reduce((a, b) => a + b, 0) / prices.length
  const squaredDiffs = prices.map(p => Math.pow(p - avg, 2))
  return Math.sqrt(squaredDiffs.reduce((a, b) => a + b, 0) / prices.length) / avg
}
