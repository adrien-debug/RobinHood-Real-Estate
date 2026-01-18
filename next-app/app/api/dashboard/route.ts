import { NextRequest, NextResponse } from 'next/server'
import { getServerClient } from '@/lib/supabase'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const dateParam = searchParams.get('date')
    const targetDate = dateParam || new Date().toISOString().split('T')[0]
    
    const supabase = getServerClient()
    
    // First, get the latest transaction date to use for "last day" KPI
    const { data: latestTxData } = await supabase
      .from('dld_transactions')
      .select('transaction_date')
      .order('transaction_date', { ascending: false })
      .limit(1)
      .single()
    
    const latestDate = latestTxData?.transaction_date || targetDate
    
    // Fetch KPIs
    const [
      lastDayTx,
      weekTx,
      monthTx,
      priceStats,
      priceStats7dAgo,
      opportunities,
      neighborhoods,
      propertyTypes,
      regimes,
      brief
    ] = await Promise.all([
      // Transactions on latest day (not today if no data)
      supabase
        .from('dld_transactions')
        .select('*', { count: 'exact', head: true })
        .eq('transaction_date', latestDate),
      
      // Transactions 7 days
      supabase
        .from('dld_transactions')
        .select('*', { count: 'exact', head: true })
        .gte('transaction_date', getDateMinusDays(latestDate, 7)),
      
      // Transactions 30 days with volume
      supabase
        .from('dld_transactions')
        .select('price_aed, price_per_sqft', { count: 'exact' })
        .gte('transaction_date', getDateMinusDays(latestDate, 30)),
      
      // Price stats (last 7 days)
      supabase
        .from('dld_transactions')
        .select('price_per_sqft')
        .gte('transaction_date', getDateMinusDays(latestDate, 7))
        .not('price_per_sqft', 'is', null),
      
      // Price stats (7-14 days ago for variation)
      supabase
        .from('dld_transactions')
        .select('price_per_sqft')
        .gte('transaction_date', getDateMinusDays(latestDate, 14))
        .lt('transaction_date', getDateMinusDays(latestDate, 7))
        .not('price_per_sqft', 'is', null),
      
      // Top opportunities
      supabase
        .from('dld_opportunities')
        .select('*')
        .order('global_score', { ascending: false })
        .limit(10),
      
      // Top neighborhoods (30 days) - direct query instead of RPC
      supabase
        .from('dld_transactions')
        .select('community, price_per_sqft')
        .gte('transaction_date', getDateMinusDays(latestDate, 30))
        .not('community', 'is', null),
      
      // Property types distribution - direct query
      supabase
        .from('dld_transactions')
        .select('rooms_bucket, price_per_sqft')
        .gte('transaction_date', getDateMinusDays(latestDate, 30))
        .not('rooms_bucket', 'is', null),
      
      // Market regimes
      supabase
        .from('dld_market_regimes')
        .select('*')
        .order('confidence_score', { ascending: false })
        .limit(5),
      
      // Daily brief
      supabase
        .from('dld_daily_briefs')
        .select('*')
        .order('brief_date', { ascending: false })
        .limit(1)
        .single()
    ])

    // Calculate stats
    const prices7d = priceStats.data?.map(p => Number(p.price_per_sqft)).filter(Boolean) as number[] || []
    const prices7to14d = priceStats7dAgo.data?.map(p => Number(p.price_per_sqft)).filter(Boolean) as number[] || []
    
    const medianPrice = prices7d.length > 0 ? calculateMedian(prices7d) : 0
    const avgPrice = prices7d.length > 0 ? prices7d.reduce((a, b) => a + b, 0) / prices7d.length : 0
    
    const volume30d = monthTx.data?.reduce((sum, tx) => sum + (Number(tx.price_aed) || 0), 0) || 0
    
    // Calculate 7d variation vs previous 7 days
    const variation7d = calculateVariation(prices7d, prices7to14d)
    
    // Process neighborhoods data
    const neighborhoodMap: Record<string, { count: number; prices: number[] }> = {}
    for (const tx of (neighborhoods.data || [])) {
      if (!tx.community) continue
      if (!neighborhoodMap[tx.community]) {
        neighborhoodMap[tx.community] = { count: 0, prices: [] }
      }
      neighborhoodMap[tx.community].count++
      if (tx.price_per_sqft) neighborhoodMap[tx.community].prices.push(Number(tx.price_per_sqft))
    }
    const topNeighborhoods = Object.entries(neighborhoodMap)
      .map(([community, data]) => ({
        community,
        transaction_count: data.count,
        avg_price_sqft: data.prices.length > 0 ? data.prices.reduce((a, b) => a + b, 0) / data.prices.length : 0
      }))
      .sort((a, b) => b.transaction_count - a.transaction_count)
      .slice(0, 10)

    // Process property types data
    const roomsMap: Record<string, { count: number; prices: number[] }> = {}
    for (const tx of (propertyTypes.data || [])) {
      if (!tx.rooms_bucket) continue
      if (!roomsMap[tx.rooms_bucket]) {
        roomsMap[tx.rooms_bucket] = { count: 0, prices: [] }
      }
      roomsMap[tx.rooms_bucket].count++
      if (tx.price_per_sqft) roomsMap[tx.rooms_bucket].prices.push(Number(tx.price_per_sqft))
    }
    const byRooms = Object.entries(roomsMap)
      .map(([rooms_bucket, data]) => ({
        rooms_bucket,
        count: data.count,
        avg_price_sqft: data.prices.length > 0 ? data.prices.reduce((a, b) => a + b, 0) / data.prices.length : 0
      }))
      .sort((a, b) => b.count - a.count)
    
    // Prepare response
    const response = {
      kpis: {
        transactions_last_day: lastDayTx.count || 0,
        transactions_7d: weekTx.count || 0,
        transactions_30d: monthTx.count || 0,
        volume_30d: volume30d,
        median_price_sqft: Math.round(medianPrice * 100) / 100,
        avg_price_sqft: Math.round(avgPrice * 100) / 100,
        variation_7d_pct: Math.round(variation7d * 100) / 100,
        avg_opportunity_score: opportunities.data?.length 
          ? Math.round((opportunities.data.reduce((sum, o) => sum + (Number(o.global_score) || 0), 0) / opportunities.data.length) * 10) / 10
          : 0
      },
      top_opportunities: opportunities.data || [],
      top_neighborhoods: topNeighborhoods,
      property_types: {
        by_rooms: byRooms
      },
      regimes: regimes.data || [],
      brief: brief.data || null,
      latest_date: latestDate,
      target_date: targetDate
    }
    
    return NextResponse.json(response)
    
  } catch (error) {
    console.error('Dashboard API error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch dashboard data' },
      { status: 500 }
    )
  }
}

// Helper functions
function getDateMinusDays(date: string, days: number): string {
  const d = new Date(date)
  d.setDate(d.getDate() - days)
  return d.toISOString().split('T')[0]
}

function calculateMedian(arr: number[]): number {
  if (arr.length === 0) return 0
  const sorted = [...arr].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2
}

function calculateVariation(current: number[], previous: number[]): number {
  if (current.length === 0 || previous.length === 0) return 0
  const avgCurrent = current.reduce((a, b) => a + b, 0) / current.length
  const avgPrevious = previous.reduce((a, b) => a + b, 0) / previous.length
  if (avgPrevious === 0) return 0
  return ((avgCurrent - avgPrevious) / avgPrevious) * 100
}
