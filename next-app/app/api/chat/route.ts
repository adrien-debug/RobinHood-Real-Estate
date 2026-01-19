import { NextRequest, NextResponse } from 'next/server'
import { getServerClient } from '@/lib/supabase'

export async function POST(request: NextRequest) {
  try {
    const { question } = await request.json()
    
    if (!question || typeof question !== 'string') {
      return NextResponse.json({ error: 'Question required' }, { status: 400 })
    }

    const supabase = getServerClient()
    const q = question.toLowerCase()

    // Determine intent and fetch relevant data
    let answer = ''

    // Yield questions
    if (q.includes('yield') || q.includes('rendement')) {
      const { data: yieldData } = await supabase
        .from('dld_rental_index')
        .select('community, avg_rent_aed, rent_count')
        .order('avg_rent_aed', { ascending: false })
        .limit(5)

      const { data: txData } = await supabase
        .from('dld_transactions')
        .select('community, price_per_sqft')
        .order('transaction_date', { ascending: false })
        .limit(500)

      // Calculate approximate yields
      const yieldByZone: Record<string, { rent: number; price: number; count: number }> = {}
      
      yieldData?.forEach(r => {
        if (r.community && r.avg_rent_aed) {
          yieldByZone[r.community] = {
            rent: r.avg_rent_aed,
            price: 0,
            count: r.rent_count || 1
          }
        }
      })

      txData?.forEach(t => {
        if (t.community && yieldByZone[t.community] && t.price_per_sqft) {
          yieldByZone[t.community].price = t.price_per_sqft
        }
      })

      const yields = Object.entries(yieldByZone)
        .filter(([_, v]) => v.price > 0 && v.rent > 0)
        .map(([zone, v]) => ({
          zone,
          yield: ((v.rent * 12) / (v.price * 100)) * 100 // Approximate
        }))
        .sort((a, b) => b.yield - a.yield)
        .slice(0, 3)

      if (yields.length > 0) {
        answer = `Les zones avec les meilleurs rendements estimés :\n${yields.map((y, i) => 
          `${i + 1}. ${y.zone}: ~${y.yield.toFixed(1)}% brut`
        ).join('\n')}`
      } else {
        answer = 'Données de rendement insuffisantes actuellement.'
      }
    }
    // Opportunities
    else if (q.includes('opportunit') || q.includes('deal') || q.includes('top')) {
      const { data } = await supabase
        .from('dld_opportunities')
        .select('community, building, global_score, discount_pct, recommended_strategy')
        .order('global_score', { ascending: false })
        .limit(3)

      if (data && data.length > 0) {
        answer = `Top ${data.length} opportunités :\n${data.map((opp, i) => 
          `${i + 1}. ${opp.community}${opp.building ? ` - ${opp.building}` : ''}\n   Score: ${Math.round(opp.global_score)} | Discount: -${opp.discount_pct?.toFixed(1)}% | ${opp.recommended_strategy}`
        ).join('\n\n')}`
      } else {
        answer = 'Aucune opportunité scorée disponible actuellement.'
      }
    }
    // Tendance / trend
    else if (q.includes('tendance') || q.includes('trend') || q.includes('semaine') || q.includes('week')) {
      const { data } = await supabase
        .from('dld_transactions')
        .select('price_per_sqft, transaction_date')
        .order('transaction_date', { ascending: false })
        .limit(200)

      if (data && data.length > 10) {
        const prices = data.map(t => t.price_per_sqft).filter(Boolean) as number[]
        const avg = prices.reduce((a, b) => a + b, 0) / prices.length
        const recentAvg = prices.slice(0, 50).reduce((a, b) => a + b, 0) / Math.min(50, prices.length)
        const trend = ((recentAvg - avg) / avg) * 100

        answer = `Tendance du marché :\n• Prix moyen récent: ${Math.round(recentAvg).toLocaleString()} AED/sqft\n• ${trend > 0 ? '📈 Hausse' : trend < 0 ? '📉 Baisse' : '➡️ Stable'} de ${Math.abs(trend).toFixed(1)}% vs moyenne\n• ${data.length} transactions analysées`
      } else {
        answer = 'Pas assez de données pour calculer la tendance.'
      }
    }
    // Volume / zones
    else if (q.includes('volume') || q.includes('zone') || q.includes('transaction')) {
      const { data } = await supabase
        .from('dld_transactions')
        .select('community')
        .order('transaction_date', { ascending: false })
        .limit(500)

      if (data) {
        const countByZone: Record<string, number> = {}
        data.forEach(t => {
          if (t.community) {
            countByZone[t.community] = (countByZone[t.community] || 0) + 1
          }
        })
        
        const topZones = Object.entries(countByZone)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 5)

        answer = `Zones avec le plus de volume (dernières transactions) :\n${topZones.map(([zone, count], i) => 
          `${i + 1}. ${zone}: ${count} transactions`
        ).join('\n')}`
      } else {
        answer = 'Données de volume non disponibles.'
      }
    }
    // Alertes
    else if (q.includes('alerte') || q.includes('alert') || q.includes('critique') || q.includes('critical')) {
      const { data } = await supabase
        .from('dld_opportunities')
        .select('community, discount_pct, global_score, recommended_strategy')
        .gte('global_score', 80)
        .order('global_score', { ascending: false })
        .limit(5)

      if (data && data.length > 0) {
        answer = `Alertes actives (score ≥80) :\n${data.map((a, i) => 
          `${i + 1}. ${a.community} - Score ${Math.round(a.global_score)}, discount -${a.discount_pct?.toFixed(1)}%\n   Stratégie: ${a.recommended_strategy}`
        ).join('\n\n')}`
      } else {
        answer = 'Aucune alerte critique active actuellement.'
      }
    }
    // Prix
    else if (q.includes('prix') || q.includes('price') || q.includes('cher') || q.includes('expensive')) {
      const { data } = await supabase
        .from('dld_transactions')
        .select('community, price_per_sqft')
        .order('price_per_sqft', { ascending: false })
        .limit(100)

      if (data && data.length > 0) {
        const priceByZone: Record<string, number[]> = {}
        data.forEach(t => {
          if (t.community && t.price_per_sqft) {
            if (!priceByZone[t.community]) priceByZone[t.community] = []
            priceByZone[t.community].push(t.price_per_sqft)
          }
        })

        const avgByZone = Object.entries(priceByZone)
          .map(([zone, prices]) => ({
            zone,
            avg: prices.reduce((a, b) => a + b, 0) / prices.length
          }))
          .sort((a, b) => b.avg - a.avg)
          .slice(0, 5)

        answer = `Zones les plus chères (prix moyen/sqft) :\n${avgByZone.map((z, i) => 
          `${i + 1}. ${z.zone}: ${Math.round(z.avg).toLocaleString()} AED/sqft`
        ).join('\n')}`
      } else {
        answer = 'Données de prix non disponibles.'
      }
    }
    // Default
    else {
      answer = `Je peux vous aider avec :\n• Rendements (yield) par zone\n• Opportunités du jour\n• Tendances du marché\n• Volumes par zone\n• Alertes actives\n• Prix par zone\n\nReformulez votre question avec ces thèmes.`
    }

    return NextResponse.json({ 
      answer,
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('Chat API error:', error)
    return NextResponse.json(
      { error: 'Failed to process question', answer: 'Erreur serveur. Veuillez réessayer.' },
      { status: 500 }
    )
  }
}
