import { NextRequest, NextResponse } from 'next/server'
import { getServerClient } from '@/lib/supabase'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const date = searchParams.get('date') || new Date().toISOString().split('T')[0]
    const strategy = searchParams.get('strategy')
    const minScore = parseInt(searchParams.get('min_score') || '0')
    const regime = searchParams.get('regime')
    const limit = parseInt(searchParams.get('limit') || '50')
    
    const supabase = getServerClient()
    
    // Build query
    let query = supabase
      .from('dld_opportunities')
      .select('*')
      .gte('global_score', minScore)
      .order('global_score', { ascending: false })
      .limit(limit)
    
    if (strategy && strategy !== 'All') {
      query = query.eq('recommended_strategy', strategy)
    }
    
    if (regime && regime !== 'All') {
      query = query.eq('market_regime', regime)
    }
    
    const { data, error } = await query
    
    if (error) throw error
    
    // Calculate stats
    const strategies: Record<string, number> = {}
    let totalDiscount = 0
    let totalScore = 0
    
    for (const opp of data || []) {
      const strat = opp.recommended_strategy || 'OTHER'
      strategies[strat] = (strategies[strat] || 0) + 1
      totalDiscount += opp.discount_pct || 0
      totalScore += opp.global_score || 0
    }
    
    const count = data?.length || 0
    
    return NextResponse.json({
      opportunities: data || [],
      stats: {
        total: count,
        by_strategy: strategies,
        avg_discount: count > 0 ? totalDiscount / count : 0,
        avg_score: count > 0 ? totalScore / count : 0
      },
      filters: {
        date,
        strategy,
        minScore,
        regime
      }
    })
    
  } catch (error) {
    console.error('Opportunities API error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch opportunities' },
      { status: 500 }
    )
  }
}
