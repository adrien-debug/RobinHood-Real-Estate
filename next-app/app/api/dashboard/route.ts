import { NextRequest, NextResponse } from 'next/server'
import { getServerClient } from '@/lib/supabase'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const dateParam = searchParams.get('date')
    const targetDate = dateParam || new Date().toISOString().split('T')[0]
    
    const supabase = getServerClient()
    
    // Fetch KPIs
    const [
      todayTx,
      weekTx,
      monthTx,
      priceStats,
      opportunities,
      neighborhoods,
      propertyTypes,
      regimes,
      brief
    ] = await Promise.all([
      // Transactions today
      supabase
        .from('transactions')
        .select('*', { count: 'exact', head: true })
        .eq('transaction_date', targetDate),
      
      // Transactions 7 days
      supabase
        .from('transactions')
        .select('*', { count: 'exact', head: true })
        .gte('transaction_date', getDateMinusDays(targetDate, 7)),
      
      // Transactions 30 days
      supabase
        .from('transactions')
        .select('price_aed, price_per_sqft', { count: 'exact' })
        .gte('transaction_date', getDateMinusDays(targetDate, 30)),
      
      // Price stats (30 days)
      supabase
        .from('transactions')
        .select('price_per_sqft')
        .gte('transaction_date', getDateMinusDays(targetDate, 30))
        .not('price_per_sqft', 'is', null),
      
      // Top opportunities
      supabase
        .from('opportunities')
        .select('*')
        .eq('detection_date', targetDate)
        .order('global_score', { ascending: false })
        .limit(10),
      
      // Top neighborhoods (30 days)
      supabase.rpc('get_top_neighborhoods', { 
        p_date: targetDate,
        p_days: 30,
        p_limit: 10 
      }),
      
      // Property types distribution
      supabase.rpc('get_property_types_distribution', {
        p_date: targetDate,
        p_days: 30
      }),
      
      // Market regimes
      supabase
        .from('market_regimes')
        .select('*')
        .eq('regime_date', targetDate)
        .order('confidence_score', { ascending: false })
        .limit(5),
      
      // Daily brief
      supabase
        .from('daily_briefs')
        .select('*')
        .eq('brief_date', targetDate)
        .single()
    ])

    // Calculate stats
    const prices = priceStats.data?.map(p => p.price_per_sqft).filter(Boolean) as number[] || []
    const medianPrice = prices.length > 0 ? calculateMedian(prices) : 0
    const avgPrice = prices.length > 0 ? prices.reduce((a, b) => a + b, 0) / prices.length : 0
    
    const volume30d = monthTx.data?.reduce((sum, tx) => sum + (tx.price_aed || 0), 0) || 0
    
    // Calculate 7d variation (simplified)
    const variation7d = calculateVariation(prices.slice(0, 100), prices.slice(100)) // Rough estimation
    
    // Prepare response
    const response = {
      kpis: {
        transactions_today: todayTx.count || 0,
        transactions_7d: weekTx.count || 0,
        transactions_30d: monthTx.count || 0,
        volume_30d: volume30d,
        median_price_sqft: medianPrice,
        avg_price_sqft: avgPrice,
        variation_7d_pct: variation7d,
        avg_opportunity_score: opportunities.data?.length 
          ? opportunities.data.reduce((sum, o) => sum + (o.global_score || 0), 0) / opportunities.data.length 
          : 0
      },
      top_opportunities: opportunities.data || [],
      top_neighborhoods: neighborhoods.data || [],
      property_types: {
        by_rooms: propertyTypes.data || []
      },
      regimes: regimes.data || [],
      brief: brief.data || null,
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
