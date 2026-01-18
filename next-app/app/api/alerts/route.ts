import { NextRequest, NextResponse } from 'next/server'
import { getServerClient } from '@/lib/supabase'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const unreadOnly = searchParams.get('unread') === 'true'
    const limit = parseInt(searchParams.get('limit') || '50')
    
    const supabase = getServerClient()
    
    let query = supabase
      .from('dld_alerts')
      .select('*')
      .eq('is_dismissed', false)
      .order('created_at', { ascending: false })
      .limit(limit)
    
    if (unreadOnly) {
      query = query.eq('is_read', false)
    }
    
    const { data, error } = await query
    
    if (error) throw error
    
    // Group by severity
    const bySeverity: Record<string, number> = {}
    for (const alert of data || []) {
      bySeverity[alert.severity] = (bySeverity[alert.severity] || 0) + 1
    }
    
    return NextResponse.json({
      alerts: data || [],
      stats: {
        total: data?.length || 0,
        unread: data?.filter(a => !a.is_read).length || 0,
        by_severity: bySeverity
      }
    })
    
  } catch (error) {
    console.error('Alerts API error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch alerts' },
      { status: 500 }
    )
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const body = await request.json()
    const { id, is_read, is_dismissed } = body
    
    const supabase = getServerClient()
    
    const updates: Record<string, boolean> = {}
    if (typeof is_read === 'boolean') updates.is_read = is_read
    if (typeof is_dismissed === 'boolean') updates.is_dismissed = is_dismissed
    
    const { error } = await supabase
      .from('dld_alerts')
      .update(updates)
      .eq('id', id)
    
    if (error) throw error
    
    return NextResponse.json({ success: true })
    
  } catch (error) {
    console.error('Alerts PATCH API error:', error)
    return NextResponse.json(
      { error: 'Failed to update alert' },
      { status: 500 }
    )
  }
}
