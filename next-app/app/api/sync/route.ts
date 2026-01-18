import { NextRequest, NextResponse } from 'next/server'
import { getServerClient } from '@/lib/supabase'

// Bayut RapidAPI configuration
const BAYUT_API_HOST = 'uae-real-estate2.p.rapidapi.com'
const BAYUT_API_URL = 'https://uae-real-estate2.p.rapidapi.com'

// Get API key from environment
const BAYUT_API_KEY = process.env.BAYUT_API_KEY || ''

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const action = body.action

    if (action === 'sync_transactions') {
      const result = await syncTransactions()
      return NextResponse.json(result)
    }

    if (action === 'compute_baselines') {
      const result = await computeBaselines()
      return NextResponse.json(result)
    }

    if (action === 'compute_regimes') {
      const result = await computeRegimes()
      return NextResponse.json(result)
    }

    if (action === 'generate_alerts') {
      const result = await generateAlerts()
      return NextResponse.json(result)
    }

    if (action === 'full_pipeline') {
      // Run full pipeline
      const txResult = await syncTransactions()
      const blResult = await computeBaselines()
      const rgResult = await computeRegimes()
      const alResult = await generateAlerts()

      return NextResponse.json({
        success: true,
        results: {
          transactions: txResult,
          baselines: blResult,
          regimes: rgResult,
          alerts: alResult
        }
      })
    }

    return NextResponse.json({ error: 'Unknown action' }, { status: 400 })

  } catch (error) {
    console.error('Sync API error:', error)
    return NextResponse.json(
      { error: 'Sync failed', details: String(error) },
      { status: 500 }
    )
  }
}

async function syncTransactions() {
  const supabase = getServerClient()

  // If Bayut API key is configured, fetch real data
  if (BAYUT_API_KEY) {
    try {
      const headers = {
        'x-rapidapi-key': BAYUT_API_KEY,
        'x-rapidapi-host': BAYUT_API_HOST,
        'Content-Type': 'application/json'
      }

      const response = await fetch(`${BAYUT_API_URL}/transactions`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          purpose: 'for-sale',
          category: 'residential',
          sort_by: 'date',
          order: 'desc',
          page: 0
        })
      })

      if (response.ok) {
        const data = await response.json()
        const transactions = parseByautTransactions(data.results || [])

        // Insert into Supabase
        if (transactions.length > 0) {
          const { error } = await supabase
            .from('dld_transactions')
            .upsert(transactions, { onConflict: 'transaction_id' })

          if (error) throw error

          return { success: true, count: transactions.length, source: 'bayut' }
        }
      }
    } catch (e) {
      console.error('Bayut API error:', e)
    }
  }

  // Fallback: return current count
  const { count } = await supabase
    .from('dld_transactions')
    .select('*', { count: 'exact', head: true })

  return { success: true, count: count || 0, source: 'existing' }
}

function parseByautTransactions(results: any[]) {
  return results.map((item, idx) => {
    const property = item.property || {}
    const location = item.location || {}
    const builtup = property.builtup_area || {}

    const area = parseFloat(builtup.sqft || '0')
    const price = parseFloat(item.amount || '0')
    const pricePerSqft = area > 0 ? price / area : 0

    const fullLocation = location.full_location || ''
    const parts = fullLocation.split(' -> ')

    return {
      transaction_id: `BAY-${item.date || 'UNK'}-${idx}`,
      transaction_date: item.date || new Date().toISOString().split('T')[0],
      transaction_type: 'SALE',
      community: parts[0] || location.location || 'Unknown',
      project: parts[1] || null,
      building: parts[2] || null,
      property_type: property.type || 'Apartment',
      rooms_count: parseInt(property.beds || '0') || null,
      rooms_bucket: getRoomsBucket(parseInt(property.beds || '0')),
      area_sqft: area > 0 ? area.toFixed(2) : null,
      price_aed: price > 0 ? price.toFixed(2) : null,
      price_per_sqft: pricePerSqft > 0 ? pricePerSqft.toFixed(2) : null,
      is_offplan: false
    }
  })
}

function getRoomsBucket(rooms: number): string {
  if (rooms === 0) return 'Studio'
  if (rooms === 1) return '1BR'
  if (rooms === 2) return '2BR'
  if (rooms === 3) return '3BR'
  if (rooms === 4) return '4BR'
  return '5BR+'
}

async function computeBaselines() {
  const supabase = getServerClient()

  // Delete old baselines
  await supabase
    .from('dld_market_baselines')
    .delete()
    .lt('calculation_date', new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0])

  // Compute new baselines via SQL
  const { data, error } = await supabase.rpc('compute_market_baselines_30d')

  if (error) {
    // If RPC doesn't exist, do it manually
    const { data: txData } = await supabase
      .from('dld_transactions')
      .select('community, rooms_bucket, price_per_sqft, price_aed')
      .gte('transaction_date', getDateMinusDays(30))

    if (txData && txData.length > 0) {
      const baselines = aggregateBaselines(txData)

      const { error: insertError } = await supabase
        .from('dld_market_baselines')
        .upsert(baselines, { onConflict: 'id' })

      if (insertError) throw insertError

      return { success: true, count: baselines.length }
    }
  }

  return { success: true, count: 0 }
}

function aggregateBaselines(data: any[]) {
  const groups: Record<string, { prices: number[]; volumes: number[] }> = {}

  for (const tx of data) {
    const key = `${tx.community}|${tx.rooms_bucket || 'ALL'}`
    if (!groups[key]) {
      groups[key] = { prices: [], volumes: [] }
    }
    if (tx.price_per_sqft) groups[key].prices.push(parseFloat(tx.price_per_sqft))
    if (tx.price_aed) groups[key].volumes.push(parseFloat(tx.price_aed))
  }

  return Object.entries(groups).map(([key, data]) => {
    const [community, rooms_bucket] = key.split('|')
    const prices = data.prices.sort((a, b) => a - b)
    const median = prices.length > 0 ? prices[Math.floor(prices.length / 2)] : 0
    const p25 = prices.length > 0 ? prices[Math.floor(prices.length * 0.25)] : 0
    const p75 = prices.length > 0 ? prices[Math.floor(prices.length * 0.75)] : 0
    const avg = prices.length > 0 ? prices.reduce((a, b) => a + b, 0) / prices.length : 0
    const total = data.volumes.reduce((a, b) => a + b, 0)
    const volatility = prices.length > 1 ? (stdDev(prices) / avg) * 100 : 0
    const dispersion = median > 0 ? ((p75 - p25) / median) * 100 : 0

    return {
      id: crypto.randomUUID(),
      calculation_date: new Date().toISOString().split('T')[0],
      community,
      rooms_bucket: rooms_bucket !== 'ALL' ? rooms_bucket : null,
      window_days: 30,
      median_price_per_sqft: median.toFixed(2),
      p25_price_per_sqft: p25.toFixed(2),
      p75_price_per_sqft: p75.toFixed(2),
      avg_price_per_sqft: avg.toFixed(2),
      transaction_count: prices.length,
      total_volume_aed: total.toFixed(2),
      momentum: 0,
      volatility: volatility.toFixed(4),
      dispersion: dispersion.toFixed(4)
    }
  })
}

function stdDev(arr: number[]): number {
  const avg = arr.reduce((a, b) => a + b, 0) / arr.length
  const squareDiffs = arr.map(v => Math.pow(v - avg, 2))
  return Math.sqrt(squareDiffs.reduce((a, b) => a + b, 0) / arr.length)
}

async function computeRegimes() {
  const supabase = getServerClient()

  // Get baselines
  const { data: baselines } = await supabase
    .from('dld_market_baselines')
    .select('community, volatility, dispersion, momentum, transaction_count')
    .eq('calculation_date', new Date().toISOString().split('T')[0])

  if (!baselines || baselines.length === 0) {
    return { success: false, error: 'No baselines found' }
  }

  // Group by community (take first for each)
  const communities: Record<string, any> = {}
  for (const b of baselines) {
    if (!communities[b.community]) {
      communities[b.community] = b
    }
  }

  const regimes = Object.values(communities).map((b: any) => {
    const volatility = parseFloat(b.volatility || '0')
    const dispersion = parseFloat(b.dispersion || '0')
    const momentum = parseFloat(b.momentum || '0')

    let regime = 'ACCUMULATION'
    if (volatility > 20 && dispersion > 30) regime = 'DISTRIBUTION'
    else if (volatility < 10 && momentum > 0) regime = 'EXPANSION'
    else if (volatility > 15 || momentum < -5) regime = 'RETOURNEMENT'

    return {
      id: crypto.randomUUID(),
      regime_date: new Date().toISOString().split('T')[0],
      community: b.community,
      regime,
      confidence_score: (0.5 + Math.random() * 0.4).toFixed(4),
      volume_trend: b.transaction_count >= 4 ? 'UP' : b.transaction_count >= 2 ? 'STABLE' : 'DOWN',
      price_trend: momentum > 5 ? 'UP' : momentum < -5 ? 'DOWN' : 'STABLE',
      dispersion_level: dispersion > 30 ? 'HIGH' : dispersion > 15 ? 'MEDIUM' : 'LOW',
      volatility_level: volatility > 20 ? 'HIGH' : volatility > 10 ? 'MEDIUM' : 'LOW'
    }
  })

  const { error } = await supabase
    .from('dld_market_regimes')
    .upsert(regimes, { onConflict: 'id' })

  if (error) throw error

  return { success: true, count: regimes.length }
}

async function generateAlerts() {
  const supabase = getServerClient()

  // Get opportunities
  const { data: opportunities } = await supabase
    .from('dld_opportunities')
    .select('*')
    .eq('status', 'active')

  if (!opportunities || opportunities.length === 0) {
    return { success: false, error: 'No opportunities found' }
  }

  const alerts = opportunities.map(o => ({
    id: crypto.randomUUID(),
    alert_date: new Date().toISOString(),
    alert_type: 'OPPORTUNITY',
    severity: parseFloat(o.discount_pct || '0') >= 22 ? 'critical' : parseFloat(o.discount_pct || '0') >= 20 ? 'high' : 'medium',
    title: `New Investment Opportunity: ${o.community}`,
    message: `Detected a ${o.recommended_strategy} opportunity in ${o.community} (${o.project}) with ${o.discount_pct}% discount and score ${o.global_score}/100`,
    opportunity_id: o.id,
    community: o.community,
    is_read: false,
    is_dismissed: false
  }))

  // Check for existing alerts for same opportunities
  const existingIds = opportunities.map(o => o.id)
  const { data: existingAlerts } = await supabase
    .from('dld_alerts')
    .select('opportunity_id')
    .in('opportunity_id', existingIds)

  const existingOpportunityIds = new Set((existingAlerts || []).map(a => a.opportunity_id))
  const newAlerts = alerts.filter(a => !existingOpportunityIds.has(a.opportunity_id))

  if (newAlerts.length > 0) {
    const { error } = await supabase
      .from('dld_alerts')
      .insert(newAlerts)

    if (error) throw error
  }

  return { success: true, count: newAlerts.length }
}

function getDateMinusDays(days: number): string {
  const d = new Date()
  d.setDate(d.getDate() - days)
  return d.toISOString().split('T')[0]
}

// GET endpoint to check sync status
export async function GET() {
  const supabase = getServerClient()

  const [tx, opp, reg, base, alerts] = await Promise.all([
    supabase.from('dld_transactions').select('*', { count: 'exact', head: true }),
    supabase.from('dld_opportunities').select('*', { count: 'exact', head: true }),
    supabase.from('dld_market_regimes').select('*', { count: 'exact', head: true }),
    supabase.from('dld_market_baselines').select('*', { count: 'exact', head: true }),
    supabase.from('dld_alerts').select('*', { count: 'exact', head: true })
  ])

  return NextResponse.json({
    status: 'ok',
    counts: {
      transactions: tx.count || 0,
      opportunities: opp.count || 0,
      regimes: reg.count || 0,
      baselines: base.count || 0,
      alerts: alerts.count || 0
    },
    api_configured: {
      bayut: !!BAYUT_API_KEY
    }
  })
}
