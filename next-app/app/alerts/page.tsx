'use client'

import { useEffect, useState } from 'react'
import { Card, CardTitle, CardSubtitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { LoadingPage } from '@/components/ui/Loading'
import { Bell, Check, X, AlertTriangle, Info, AlertCircle } from 'lucide-react'
import type { Alert } from '@/lib/types/database'
import { useAutoRefresh } from '@/lib/useAutoRefresh'

interface AlertsData {
  alerts: Alert[]
  stats: {
    total: number
    unread: number
    by_severity: Record<string, number>
  }
}

export default function AlertsPage() {
  const AUTO_REFRESH_MS = 5000
  const [data, setData] = useState<AlertsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'unread'>('all')

  useEffect(() => {
    fetchAlerts()
  }, [])

  const fetchAlerts = async () => {
    try {
      setLoading(true)
      const res = await fetch('/api/alerts')
      const json = await res.json()
      setData(json)
    } catch (err) {
      console.error('Failed to fetch alerts:', err)
    } finally {
      setLoading(false)
    }
  }

  const markAsRead = async (id: number) => {
    try {
      await fetch('/api/alerts', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, is_read: true })
      })
      fetchAlerts()
    } catch (err) {
      console.error('Failed to mark as read:', err)
    }
  }

  const dismissAlert = async (id: number) => {
    try {
      await fetch('/api/alerts', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, is_dismissed: true })
      })
      fetchAlerts()
    } catch (err) {
      console.error('Failed to dismiss:', err)
    }
  }

  useAutoRefresh({
    intervalMs: AUTO_REFRESH_MS,
    onTick: fetchAlerts
  })

  if (loading && !data) return <LoadingPage />
  if (!data) return <div className="text-text-muted p-4">No data available</div>

  const { alerts, stats } = data

  const filteredAlerts = filter === 'unread' 
    ? alerts.filter(a => !a.is_read) 
    : alerts

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <AlertCircle className="w-5 h-5 text-danger" />
      case 'high': return <AlertTriangle className="w-5 h-5 text-warning" />
      case 'medium': return <Info className="w-5 h-5 text-info" />
      default: return <Bell className="w-5 h-5 text-text-muted" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#EF4444'
      case 'high': return '#F59E0B'
      case 'medium': return '#3B82F6'
      default: return '#6B7280'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Alerts</h1>
          <p className="text-text-muted text-sm mt-1">Market notifications and opportunities</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-background-secondary rounded-lg p-1">
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
                filter === 'all' ? 'bg-accent text-background' : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              All ({stats.total})
            </button>
            <button
              onClick={() => setFilter('unread')}
              className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
                filter === 'unread' ? 'bg-accent text-background' : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              Unread ({stats.unread})
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="text-center">
          <p className="text-2xl font-bold text-text-primary">{stats.total}</p>
          <p className="text-xs text-text-muted">Total Alerts</p>
        </Card>
        <Card className="text-center">
          <p className="text-2xl font-bold text-danger">{stats.by_severity.critical || 0}</p>
          <p className="text-xs text-text-muted">Critical</p>
        </Card>
        <Card className="text-center">
          <p className="text-2xl font-bold text-warning">{stats.by_severity.high || 0}</p>
          <p className="text-xs text-text-muted">High</p>
        </Card>
        <Card className="text-center">
          <p className="text-2xl font-bold text-info">{stats.by_severity.medium || 0}</p>
          <p className="text-xs text-text-muted">Medium</p>
        </Card>
      </div>

      {/* Alerts List */}
      <div className="space-y-3">
        {filteredAlerts.length === 0 ? (
          <Card className="text-center py-12">
            <Bell className="w-12 h-12 text-text-muted mx-auto mb-4" />
            <p className="text-text-muted">No alerts to display</p>
          </Card>
        ) : (
          filteredAlerts.map((alert) => (
            <Card 
              key={alert.id}
              accent
              accentColor={getSeverityColor(alert.severity)}
              className={`${!alert.is_read ? 'bg-background-hover' : ''}`}
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 mt-1">
                  {getSeverityIcon(alert.severity)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-text-primary">{alert.title}</h3>
                    <Badge 
                      variant={
                        alert.severity === 'critical' ? 'danger' : 
                        alert.severity === 'high' ? 'warning' : 
                        alert.severity === 'medium' ? 'info' : 'default'
                      }
                    >
                      {alert.severity}
                    </Badge>
                    {!alert.is_read && (
                      <span className="w-2 h-2 rounded-full bg-accent" />
                    )}
                  </div>
                  <p className="text-sm text-text-secondary mb-2">{alert.message}</p>
                  <div className="flex items-center gap-4 text-xs text-text-muted">
                    <span>{alert.alert_type}</span>
                    {alert.community && <span>{alert.community}</span>}
                    {alert.created_at && (
                      <span>{new Date(alert.created_at).toLocaleDateString()}</span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {!alert.is_read && (
                    <button
                      onClick={() => alert.id && markAsRead(alert.id)}
                      className="p-2 rounded-lg text-text-muted hover:text-success hover:bg-success/10 transition-colors"
                      title="Mark as read"
                    >
                      <Check className="w-4 h-4" />
                    </button>
                  )}
                  <button
                    onClick={() => alert.id && dismissAlert(alert.id)}
                    className="p-2 rounded-lg text-text-muted hover:text-danger hover:bg-danger/10 transition-colors"
                    title="Dismiss"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
