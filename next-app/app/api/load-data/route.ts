import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'
import fs from 'fs'
import path from 'path'
import { parse } from 'csv-parse/sync'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export async function POST(request: Request) {
  try {
    const { action } = await request.json()

    if (action === 'load_transactions') {
      // Charger le CSV
      const csvPath = path.join(process.cwd(), '..', 'data', 'transactions_12months.csv')
      
      if (!fs.existsSync(csvPath)) {
        return NextResponse.json({ 
          error: 'CSV file not found',
          path: csvPath 
        }, { status: 404 })
      }

      const fileContent = fs.readFileSync(csvPath, 'utf-8')
      const records = parse(fileContent, {
        columns: true,
        skip_empty_lines: true
      })

      console.log(`Loaded ${records.length} records from CSV`)

      // Insérer par batch de 50
      const batchSize = 50
      let totalInserted = 0
      let totalErrors = 0

      for (let i = 0; i < records.length; i += batchSize) {
        const batch = records.slice(i, i + batchSize)

        try {
          const { data, error } = await supabase
            .from('dld_transactions')
            .upsert(
              batch.map((record: any) => ({
                transaction_id: record.transaction_id,
                transaction_date: record.transaction_date,
                transaction_type: record.transaction_type,
                community: record.community,
                project: record.project || null,
                building: record.building || null,
                property_type: record.property_type,
                rooms_bucket: record.rooms_bucket || null,
                area_sqft: record.area_sqft ? parseFloat(record.area_sqft) : null,
                price_aed: parseFloat(record.price_aed),
                price_per_sqft: record.price_per_sqft ? parseFloat(record.price_per_sqft) : null,
                is_offplan: record.is_offplan === 'True' || record.is_offplan === 'true'
              })),
              { onConflict: 'transaction_id' }
            )

          if (error) {
            console.error(`Batch ${i / batchSize + 1} error:`, error)
            totalErrors += batch.length
          } else {
            totalInserted += batch.length
            console.log(`Batch ${i / batchSize + 1}: ${batch.length} records`)
          }
        } catch (err) {
          console.error(`Batch ${i / batchSize + 1} exception:`, err)
          totalErrors += batch.length
        }
      }

      return NextResponse.json({
        success: true,
        totalRecords: records.length,
        inserted: totalInserted,
        errors: totalErrors
      })
    }

    return NextResponse.json({ error: 'Invalid action' }, { status: 400 })

  } catch (error: any) {
    console.error('Load data error:', error)
    return NextResponse.json({ 
      error: error.message || 'Internal server error' 
    }, { status: 500 })
  }
}

export async function GET() {
  try {
    // Compter les transactions
    const { count, error } = await supabase
      .from('dld_transactions')
      .select('*', { count: 'exact', head: true })

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    // Récupérer quelques exemples
    const { data: samples } = await supabase
      .from('dld_transactions')
      .select('*')
      .order('transaction_date', { ascending: false })
      .limit(5)

    // Statistiques de base
    const { data: stats } = await supabase
      .from('dld_transactions')
      .select('price_aed, area_sqft, property_type, community')

    let avgPrice = 0
    let avgArea = 0
    const typeCounts: Record<string, number> = {}
    const communityCounts: Record<string, number> = {}

    if (stats) {
      avgPrice = stats.reduce((sum, tx) => sum + (tx.price_aed || 0), 0) / stats.length
      avgArea = stats.reduce((sum, tx) => sum + (tx.area_sqft || 0), 0) / stats.length

      stats.forEach(tx => {
        typeCounts[tx.property_type] = (typeCounts[tx.property_type] || 0) + 1
        communityCounts[tx.community] = (communityCounts[tx.community] || 0) + 1
      })
    }

    return NextResponse.json({
      count,
      avgPrice,
      avgArea,
      topTypes: Object.entries(typeCounts)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 5)
        .map(([type, count]) => ({ type, count })),
      topCommunities: Object.entries(communityCounts)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 10)
        .map(([community, count]) => ({ community, count })),
      samples
    })

  } catch (error: any) {
    console.error('Get data error:', error)
    return NextResponse.json({ 
      error: error.message || 'Internal server error' 
    }, { status: 500 })
  }
}
