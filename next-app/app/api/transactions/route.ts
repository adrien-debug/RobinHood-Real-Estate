import { NextRequest, NextResponse } from 'next/server'
import { getServerClient } from '@/lib/supabase'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const date = searchParams.get('date') || new Date().toISOString().split('T')[0]
    const community = searchParams.get('community')
    const rooms = searchParams.get('rooms')
    const minPrice = searchParams.get('min_price')
    const daysParam = searchParams.get('days')
    const parsedDays = daysParam ? parseInt(daysParam, 10) : 7
    const days = Number.isFinite(parsedDays) && parsedDays > 0 && parsedDays <= 365 ? parsedDays : 7
    const limit = parseInt(searchParams.get('limit') || '50')
    const offset = parseInt(searchParams.get('offset') || '0')
    
    const supabase = getServerClient()
    
    // Build query
    let query = supabase
      .from('dld_transactions')
      .select('*', { count: 'exact' })
      .gte('transaction_date', getDateMinusDays(date, days))
      .order('price_per_sqft', { ascending: false })
    
    if (community && community !== 'All') {
      query = query.eq('community', community)
    }
    
    if (rooms && rooms !== 'All') {
      query = query.eq('rooms_bucket', rooms)
    }
    
    if (minPrice) {
      query = query.gte('price_aed', parseInt(minPrice))
    }
    
    query = query.range(offset, offset + limit - 1)
    
    if (daysParam && days !== parsedDays) {
      console.warn('Transactions API: invalid days param, defaulting to 7', {
        daysParam
      })
    }
    
    const statsQuery = supabase
      .from('dld_transactions')
      .select('price_aed, price_per_sqft')
      .gte('transaction_date', getDateMinusDays(date, days))
    
    if (community && community !== 'All') {
      statsQuery.eq('community', community)
    }
    
    if (rooms && rooms !== 'All') {
      statsQuery.eq('rooms_bucket', rooms)
    }
    
    if (minPrice) {
      statsQuery.gte('price_aed', parseInt(minPrice))
    }
    
    const [{ data, error, count }, { data: statsData, error: statsError }] = await Promise.all([
      query,
      statsQuery
    ])
    
    if (error) throw error
    if (statsError) {
      console.error('Transactions stats query error:', statsError)
    }
    
    // Calculate summary stats
    const statsSource = statsError ? data : statsData
    const prices = statsSource?.map(t => t.price_per_sqft).filter(Boolean) as number[] || []
    const totalVolume = statsSource?.reduce((sum, t) => sum + (t.price_aed || 0), 0) || 0
    const avgPrice = prices.length > 0 ? prices.reduce((a, b) => a + b, 0) / prices.length : 0
    const belowMarket = statsSource?.filter(t => (t.price_per_sqft || 0) < avgPrice * 0.9).length || 0
    
    return NextResponse.json({
      transactions: data || [],
      total: count || 0,
      stats: {
        total_volume: totalVolume,
        avg_price_sqft: avgPrice,
        below_market_count: belowMarket,
        below_market_pct: data?.length ? (belowMarket / data.length) * 100 : 0
      },
      filters: {
        date,
        community,
        rooms,
        minPrice,
        days
      }
    })
    
  } catch (error) {
    console.error('Transactions API error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch transactions' },
      { status: 500 }
    )
  }
}

// Get communities list
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const action = body.action
    
    const supabase = getServerClient()
    
    if (action === 'get_communities') {
      const { data, error } = await supabase
        .from('dld_transactions')
        .select('community')
        .not('community', 'is', null)
        .order('community')
      
      if (error) throw error
      
      // Get unique communities
      const communities = [...new Set(data?.map(d => d.community))]
      
      return NextResponse.json({ communities })
    }
    
    if (action === 'get_historical') {
      const days = body.days || 90
      const { data, error } = await supabase
        .from('dld_transactions')
        .select('transaction_date, price_per_sqft, area_sqft')
        .gte('transaction_date', getDateMinusDays(new Date().toISOString().split('T')[0], days))
        .not('price_per_sqft', 'is', null)
        .order('transaction_date')
      
      if (error) throw error
      
      // Group by week
      const weeklyData = groupByWeek(data || [])
      
      return NextResponse.json({ historical: weeklyData })
    }
    
    return NextResponse.json({ error: 'Unknown action' }, { status: 400 })
    
  } catch (error) {
    console.error('Transactions POST API error:', error)
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    )
  }
}

function getDateMinusDays(date: string, days: number): string {
  const d = new Date(date)
  d.setDate(d.getDate() - days)
  return d.toISOString().split('T')[0]
}

function groupByWeek(data: Array<{ transaction_date: string; price_per_sqft: number | null }>) {
  const weeks: Record<string, { prices: number[]; count: number }> = {}
  
  for (const item of data) {
    const date = new Date(item.transaction_date)
    const weekStart = new Date(date)
    weekStart.setDate(date.getDate() - date.getDay())
    const weekKey = weekStart.toISOString().split('T')[0]
    
    if (!weeks[weekKey]) {
      weeks[weekKey] = { prices: [], count: 0 }
    }
    
    if (item.price_per_sqft) {
      weeks[weekKey].prices.push(item.price_per_sqft)
      weeks[weekKey].count++
    }
  }
  
  return Object.entries(weeks).map(([week, data]) => ({
    week,
    avg_price: data.prices.length > 0 ? data.prices.reduce((a, b) => a + b, 0) / data.prices.length : 0,
    volume: data.count
  })).sort((a, b) => a.week.localeCompare(b.week))
}
