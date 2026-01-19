'use client'

import { useEffect, useState } from 'react'
import { Card, CardSubtitle, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { AlertCircle, AlertTriangle, Bell, Info } from 'lucide-react'
import { cn } from '@/lib/utils'

interface AlertItem {
  id?: number
  alert_type?: string
  community?: string
  message?: string
  severity?: string
  created_at?: string
}

interface AlertsBannerProps {
  title?: string
  limit?: number
  className?: string
}

const severityStyles: Record<string, { color: string; bg: string; icon: JSX.Element }> = {
  critical: {
    color: '#EF4444',
    bg: 'from-red-500/20 via-red-500/10 to-transparent',
    icon: <AlertCircle className="w-4 h-4 text-danger" />
  },
  high: {
    color: '#F59E0B',
    bg: 'from-amber-500/20 via-amber-500/10 to-transparent',
    icon: <AlertTriangle className="w-4 h-4 text-warning" />
  },
  medium: {
    color: '#3B82F6',
    bg: 'from-blue-500/20 via-blue-500/10 to-transparent',
    icon: <Info className="w-4 h-4 text-info" />
  },
  low: {
    color: '#6B7280',
    bg: 'from-slate-500/20 via-slate-500/10 to-transparent',
    icon: <Bell className="w-4 h-4 text-text-muted" />
  }
}

export function AlertsBanner({ title = 'Alerts', limit = 5, className }: AlertsBannerProps) {
  const [alerts, setAlerts] = useState<AlertItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        setLoading(true)
        const res = await fetch(`/api/alerts?limit=${limit}`)
        const json = await res.json()
        setAlerts(json.alerts || [])
      } catch (err) {
        console.error('Alerts banner fetch error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchAlerts()
  }, [limit])

  return (
    <Card className={cn('relative overflow-hidden', className)}>
      <div className="flex items-center justify-between gap-4">
        <div>
          <CardTitle>{title}</CardTitle>
          <CardSubtitle>Alertes harmonisées</CardSubtitle>
        </div>
        <Badge variant="default">{alerts.length}</Badge>
      </div>
      <div className="mt-4 flex gap-3 overflow-x-auto pb-1">
        {loading ? (
          <div className="text-sm text-text-muted">Chargement des alertes...</div>
        ) : alerts.length ? (
          alerts.map((alert, index) => {
            const severity = (alert.severity || 'low').toLowerCase()
            const style = severityStyles[severity] || severityStyles.low
            return (
              <div
                key={alert.id ?? index}
                className={cn(
                  'min-w-[220px] rounded-xl border border-border/70 bg-gradient-to-br p-3',
                  style.bg
                )}
                style={{ borderLeft: `3px solid ${style.color}` }}
              >
                <div className="flex items-center gap-2">
                  {style.icon}
                  <span className="text-xs uppercase tracking-wider text-text-muted">
                    {alert.alert_type || 'Alert'}
                  </span>
                </div>
                <div className="mt-2 text-sm text-text-primary font-semibold line-clamp-1">
                  {alert.community || 'Zone globale'}
                </div>
                <div className="mt-1 text-xs text-text-secondary line-clamp-2">
                  {alert.message || 'Signal détecté sur le marché.'}
                </div>
              </div>
            )
          })
        ) : (
          <div className="text-sm text-text-muted">Aucune alerte active</div>
        )}
      </div>
    </Card>
  )
}
