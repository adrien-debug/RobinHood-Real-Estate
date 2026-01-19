'use client'

import { useEffect, useState } from 'react'
import { Card, CardSubtitle, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { AlertCircle, AlertTriangle, Bell, Info } from 'lucide-react'

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

const getSeverityIcon = (severity: string) => {
  switch (severity?.toLowerCase()) {
    case 'critical':
      return <AlertCircle className="w-4 h-4 text-danger" />
    case 'high':
      return <AlertTriangle className="w-4 h-4 text-warning" />
    case 'medium':
      return <Info className="w-4 h-4 text-info" />
    default:
      return <Bell className="w-4 h-4 text-text-muted" />
  }
}

const getSeverityBadge = (severity: string) => {
  switch (severity?.toLowerCase()) {
    case 'critical':
      return 'danger'
    case 'high':
      return 'warning'
    case 'medium':
      return 'info'
    default:
      return 'default'
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
        console.error('Alerts fetch error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchAlerts()
  }, [limit])

  return (
    <Card className={className}>
      <div className="flex items-center justify-between">
        <CardTitle>{title}</CardTitle>
        <Badge variant="default">{alerts.length}</Badge>
      </div>
      <CardSubtitle>Dernières alertes</CardSubtitle>
      
      <div className="mt-4 space-y-2">
        {loading ? (
          <div className="text-sm text-text-muted">Chargement...</div>
        ) : alerts.length ? (
          alerts.map((alert, index) => (
            <div
              key={alert.id ?? index}
              className="flex items-start gap-3 p-3 rounded-lg bg-background-secondary border border-border"
            >
              <div className="mt-0.5">{getSeverityIcon(alert.severity || 'low')}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-text-primary truncate">
                    {alert.community || 'Marché global'}
                  </span>
                  <Badge variant={getSeverityBadge(alert.severity || 'low') as 'danger' | 'warning' | 'info' | 'default'}>
                    {alert.severity || 'info'}
                  </Badge>
                </div>
                <p className="text-xs text-text-secondary mt-1 line-clamp-2">
                  {alert.message || 'Signal détecté.'}
                </p>
              </div>
            </div>
          ))
        ) : (
          <div className="text-sm text-text-muted">Aucune alerte</div>
        )}
      </div>
    </Card>
  )
}
