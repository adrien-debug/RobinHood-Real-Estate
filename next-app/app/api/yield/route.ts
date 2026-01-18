import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

export async function GET() {
  try {
    // Fetch rental data from rental_index
    const { data: rentalData, error: rentalError } = await supabase
      .from('rental_index')
      .select('*')
      .order('period_date', { ascending: false })
      .limit(1000)

    if (rentalError) {
      console.error('Rental index error:', rentalError)
    }

    // Fetch recent transactions for price data
    const { data: txData, error: txError } = await supabase
      .from('dld_transactions')
      .select('community, price_per_sqft, area_sqft, rooms_bucket')
      .gte('transaction_date', new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString())
      .not('community', 'is', null)
      .not('price_per_sqft', 'is', null)

    if (txError) {
      console.error('Transactions error:', txError)
      return NextResponse.json({ error: txError.message }, { status: 500 })
    }

    // Group transactions by community
    const txByComm: Record<string, { prices: number[], areas: number[], count: number }> = {}
    txData?.forEach(tx => {
      const comm = tx.community
      if (!txByComm[comm]) {
        txByComm[comm] = { prices: [], areas: [], count: 0 }
      }
      txByComm[comm].prices.push(tx.price_per_sqft)
      if (tx.area_sqft) txByComm[comm].areas.push(tx.area_sqft)
      txByComm[comm].count++
    })

    // Group rental data by community (latest period)
    const rentalByComm: Record<string, { avg_rent: number, median_rent: number, rent_count: number }> = {}
    rentalData?.forEach(r => {
      const comm = r.community
      if (!comm) return
      if (!rentalByComm[comm]) {
        rentalByComm[comm] = {
          avg_rent: r.avg_rent_aed || 0,
          median_rent: r.median_rent_aed || 0,
          rent_count: r.rent_count || 0
        }
      } else {
        // Aggregate if multiple entries
        rentalByComm[comm].avg_rent += r.avg_rent_aed || 0
        rentalByComm[comm].median_rent += r.median_rent_aed || 0
        rentalByComm[comm].rent_count += r.rent_count || 0
      }
    })

    // Calculate yields
    const zones = Object.keys(txByComm).map(community => {
      const tx = txByComm[community]
      const rental = rentalByComm[community]

      const avgPriceSqft = tx.prices.reduce((a, b) => a + b, 0) / tx.prices.length
      const avgArea = tx.areas.length > 0 
        ? tx.areas.reduce((a, b) => a + b, 0) / tx.areas.length 
        : 1000 // default 1000 sqft

      const avgPropertyPrice = avgPriceSqft * avgArea

      // Use real rental data if available, otherwise estimate
      let annualRent = 0
      let grossYield = 0
      let dataSource = 'estimated'

      if (rental && rental.avg_rent > 0) {
        annualRent = rental.avg_rent * 12
        grossYield = (annualRent / avgPropertyPrice) * 100
        dataSource = 'real'
      } else {
        // Fallback: estimate 5-7% yield based on Dubai market
        const estimatedYield = 0.06 // 6% base
        annualRent = avgPropertyPrice * estimatedYield
        grossYield = estimatedYield * 100
        dataSource = 'estimated'
      }

      return {
        community,
        avg_price_sqft: avgPriceSqft,
        avg_area_sqft: avgArea,
        avg_property_price: avgPropertyPrice,
        annual_rent: annualRent,
        monthly_rent: annualRent / 12,
        gross_yield: grossYield,
        transaction_count: tx.count,
        rent_data_available: dataSource === 'real',
        data_source: dataSource
      }
    })

    // Sort by yield
    zones.sort((a, b) => b.gross_yield - a.gross_yield)

    // Calculate summary
    const yields = zones.map(z => z.gross_yield)
    const summary = {
      avg_yield: yields.length > 0 ? yields.reduce((a, b) => a + b, 0) / yields.length : 0,
      max_yield: yields.length > 0 ? Math.max(...yields) : 0,
      min_yield: yields.length > 0 ? Math.min(...yields) : 0,
      zones_with_real_data: zones.filter(z => z.rent_data_available).length,
      zones_with_estimated_data: zones.filter(z => !z.rent_data_available).length,
      total_zones: zones.length
    }

    return NextResponse.json({
      zones,
      summary,
      metadata: {
        rental_records: rentalData?.length || 0,
        transaction_records: txData?.length || 0,
        calculation_date: new Date().toISOString()
      }
    })

  } catch (error) {
    console.error('Yield API error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    )
  }
}
