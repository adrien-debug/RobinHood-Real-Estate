'use client'

import { useEffect, useState } from 'react'
import { Card, CardTitle, CardSubtitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { DatePicker } from '@/components/ui/DatePicker'
import { AlertCircle, AlertTriangle, Bell, Info, History, Calendar } from 'lucide-react'
import { format, subDays, isAfter, isBefore, parseISO } from 'date-fns'

interface HistoryAlert {
  id?: number
  alert_type?: string
  community?: string
  title?: string
  message?: string
  severity?: string
  created_at?: string
  is_read?: boolean
}

interface AlertsHistoryProps {
  className?: string
}

export function AlertsHistory({ className }: AlertsHistoryProps) {
  const [alerts, setAlerts] = useState<HistoryAlert[]>([])
  const [loading, setLoading] = useState(true)
  const [startDate, setStartDate] = useState<string>(format(subDays(new Date(), 30), 'yyyy-MM-dd'))
  const [endDate, setEndDate] = useState<string>(format(new Date(), 'yyyy-MM-dd'))

  useEffect(() => {
    fetchHistory()
  }, [startDate, endDate])

  const fetchHistory = async () => {
    try {
      setLoading(true)
      const res = await fetch(`/api/alerts?limit=100`)
      const json = await res.json()
      
      // Filter by date range
      const filtered = (json.alerts || []).filter((alert: HistoryAlert) => {
        if (!alert.created_at) return true
        const alertDate = parseISO(alert.created_at)
        const start = parseISO(startDate)
        const end = parseISO(endDate)
        return !isBefore(alertDate, start) && !isAfter(alertDate, end)
      })
      
      setAlerts(filtered)
    } catch (err) {
      console.error('History fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return <AlertCircle className="w-3 h-3 text-danger" />
      case 'high':
        return <AlertTriangle className="w-3 h-3 text-warning" />
      case 'medium':
        return <Info className="w-3 h-3 text-info" />
      default:
        return <Bell className="w-3 h-3 text-text-muted" />
    }
  }

  const getSeverityBadge = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'danger'
      case 'high': return 'warning'
      case 'medium': return 'info'
      default: return 'default'
    }
  }

  // Group alerts by date
  const groupedAlerts = alerts.reduce((acc, alert) => {
    const date = alert.created_at 
      ? format(parseISO(alert.created_at), 'yyyy-MM-dd')
      : 'unknown'
    if (!acc[date]) acc[date] = []
    acc[date].push(alert)
    return acc
  }, {} as Record<string, HistoryAlert[]>)

  const sortedDates = Object.keys(groupedAlerts).sort((a, b) => b.localeCompare(a))

  return (
    <Card className={className}>
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-text-muted" />
          <CardTitle>Historique des Alertes</CardTitle>
        </div>
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-text-muted" />
          <DatePicker
            value={startDate}
            onChange={setStartDate}
            className="w-36"
          />
          <span className="text-text-muted">→</span>
          <DatePicker
            value={endDate}
            onChange={setEndDate}
            className="w-36"
          />
        </div>
      </div>
      <CardSubtitle>Timeline des alertes passées ({alerts.length} alertes)</CardSubtitle>

      <div className="mt-4 relative">
        {loading ? (
          <div className="text-sm text-text-muted py-8 text-center">Chargement...</div>
        ) : sortedDates.length === 0 ? (
          <div className="text-sm text-text-muted py-8 text-center">Aucune alerte sur cette période</div>
        ) : (
          <div className="space-y-4">
            {sortedDates.map((date) => (
              <div key={date} className="relative pl-6">
                {/* Timeline line */}
                <div className="absolute left-2 top-0 bottom-0 w-px bg-border" />
                
                {/* Date marker */}
                <div className="absolute left-0 top-0 w-4 h-4 rounded-full bg-accent border-2 border-background" />
                
                {/* Date label */}
                <div className="text-xs font-semibold text-text-muted mb-2">
                  {format(parseISO(date), 'dd MMM yyyy')}
                </div>
                
                {/* Alerts for this date */}
                <div className="space-y-2">
                  {groupedAlerts[date].map((alert, idx) => (
                    <div
                      key={alert.id ?? idx}
                      className="flex items-start gap-2 p-2 rounded-lg bg-background-secondary border border-border text-sm"
                    >
                      <div className="mt-0.5">{getSeverityIcon(alert.severity || 'low')}</div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-text-primary truncate">
                            {alert.community || alert.title || 'Signal'}
                          </span>
                          <Badge variant={getSeverityBadge(alert.severity || 'low') as 'danger' | 'warning' | 'info' | 'default'}>
                            {alert.severity || 'info'}
                          </Badge>
                          {alert.created_at && (
                            <span className="text-xs text-text-muted ml-auto">
                              {format(parseISO(alert.created_at), 'HH:mm')}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-text-secondary mt-0.5 line-clamp-1">
                          {alert.message || 'Signal détecté.'}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Card>
  )
}
