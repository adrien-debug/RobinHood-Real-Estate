'use client'

import { useState } from 'react'
import { Card, CardTitle, CardSubtitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { 
  Database, 
  RefreshCw, 
  Play, 
  Settings, 
  Key, 
  CheckCircle, 
  XCircle,
  AlertTriangle
} from 'lucide-react'

interface PipelineStep {
  name: string
  status: 'idle' | 'running' | 'success' | 'error'
  message?: string
}

export default function AdminPage() {
  const [isRunning, setIsRunning] = useState(false)
  const [pipelineSteps, setPipelineSteps] = useState<PipelineStep[]>([
    { name: 'Ingest Transactions', status: 'idle' },
    { name: 'Ingest Mortgages', status: 'idle' },
    { name: 'Compute Features', status: 'idle' },
    { name: 'Compute Baselines', status: 'idle' },
    { name: 'Compute Regimes', status: 'idle' },
    { name: 'Compute KPIs', status: 'idle' },
    { name: 'Detect Anomalies', status: 'idle' },
    { name: 'Compute Scores', status: 'idle' },
    { name: 'Generate Brief', status: 'idle' },
  ])

  const [dbStatus, setDbStatus] = useState<'connected' | 'disconnected' | 'unknown'>('unknown')
  const [apiStatus, setApiStatus] = useState<Record<string, boolean>>({
    bayut: false,
    dld: false,
    propertyfinder: false,
    supabase: false,
  })

  const runPipeline = async () => {
    setIsRunning(true)
    
    const stepActions = [
      { name: 'Ingest Transactions', action: 'sync_transactions' },
      { name: 'Ingest Mortgages', action: null },
      { name: 'Compute Features', action: null },
      { name: 'Compute Baselines', action: 'compute_baselines' },
      { name: 'Compute Regimes', action: 'compute_regimes' },
      { name: 'Compute KPIs', action: null },
      { name: 'Detect Anomalies', action: null },
      { name: 'Compute Scores', action: null },
      { name: 'Generate Brief', action: 'generate_alerts' },
    ]
    
    for (let i = 0; i < pipelineSteps.length; i++) {
      setPipelineSteps(prev => prev.map((step, idx) => 
        idx === i ? { ...step, status: 'running' } : step
      ))
      
      let success = true
      let message = 'Completed'
      
      const action = stepActions[i].action
      if (action) {
        try {
          const response = await fetch('/api/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action })
          })
          const result = await response.json()
          if (result.error) {
            success = false
            message = result.error
          } else {
            message = `Completed (${result.count || 0} items)`
          }
        } catch (e) {
          success = false
          message = 'API call failed'
        }
      } else {
        // Skip steps without actions
        await new Promise(resolve => setTimeout(resolve, 500))
        message = 'Skipped'
      }
      
      setPipelineSteps(prev => prev.map((step, idx) => 
        idx === i ? { 
          ...step, 
          status: success ? 'success' : 'error',
          message
        } : step
      ))
      
      if (!success) break
    }
    
    setIsRunning(false)
  }

  const checkConnections = async () => {
    try {
      const response = await fetch('/api/sync')
      const data = await response.json()
      
      setDbStatus(data.status === 'ok' ? 'connected' : 'disconnected')
      setApiStatus({
        bayut: data.api_configured?.bayut || false,
        dld: false,
        propertyfinder: false,
        supabase: true,
      })
    } catch {
      setDbStatus('disconnected')
    }
  }

  const getStatusIcon = (status: PipelineStep['status']) => {
    switch (status) {
      case 'running': return <RefreshCw className="w-4 h-4 text-info animate-spin" />
      case 'success': return <CheckCircle className="w-4 h-4 text-success" />
      case 'error': return <XCircle className="w-4 h-4 text-danger" />
      default: return <div className="w-4 h-4 rounded-full border-2 border-text-muted" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Administration</h1>
        <p className="text-text-muted text-sm mt-1">System configuration and data pipeline</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Database Status */}
        <Card>
          <CardTitle>Database Status</CardTitle>
          <div className="mt-4 space-y-4">
            <div className="flex items-center justify-between p-3 bg-background-secondary rounded-lg">
              <div className="flex items-center gap-3">
                <Database className="w-5 h-5 text-text-muted" />
                <span className="text-text-primary">Supabase PostgreSQL</span>
              </div>
              <Badge 
                variant={dbStatus === 'connected' ? 'success' : dbStatus === 'disconnected' ? 'danger' : 'default'}
              >
                {dbStatus === 'connected' ? 'Connected' : dbStatus === 'disconnected' ? 'Disconnected' : 'Unknown'}
              </Badge>
            </div>
            
            <button
              onClick={checkConnections}
              className="btn-secondary w-full"
            >
              <RefreshCw className="w-4 h-4" />
              Check Connections
            </button>
          </div>
        </Card>

        {/* API Status */}
        <Card>
          <CardTitle>API Connections</CardTitle>
          <div className="mt-4 space-y-2">
            {Object.entries(apiStatus).map(([api, status]) => (
              <div 
                key={api}
                className="flex items-center justify-between p-3 bg-background-secondary rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <Key className="w-4 h-4 text-text-muted" />
                  <span className="text-text-primary capitalize">{api} API</span>
                </div>
                {status ? (
                  <CheckCircle className="w-5 h-5 text-success" />
                ) : (
                  <XCircle className="w-5 h-5 text-danger" />
                )}
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Data Pipeline */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <div>
            <CardTitle>Data Pipeline</CardTitle>
            <CardSubtitle>Execute daily data processing</CardSubtitle>
          </div>
          <button
            onClick={runPipeline}
            disabled={isRunning}
            className="btn-primary"
          >
            {isRunning ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Running...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Run Pipeline
              </>
            )}
          </button>
        </div>

        <div className="space-y-2">
          {pipelineSteps.map((step, index) => (
            <div 
              key={index}
              className={`flex items-center justify-between p-3 rounded-lg transition-colors ${
                step.status === 'running' ? 'bg-info/10 border border-info/30' :
                step.status === 'success' ? 'bg-success/10' :
                step.status === 'error' ? 'bg-danger/10' :
                'bg-background-secondary'
              }`}
            >
              <div className="flex items-center gap-3">
                {getStatusIcon(step.status)}
                <span className="text-text-primary">{step.name}</span>
              </div>
              {step.message && (
                <span className={`text-xs ${step.status === 'error' ? 'text-danger' : 'text-text-muted'}`}>
                  {step.message}
                </span>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Configuration */}
      <Card>
        <CardTitle>Configuration</CardTitle>
        <CardSubtitle>Environment settings</CardSubtitle>
        
        <div className="mt-4 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-background-secondary rounded-lg">
              <p className="text-xs text-text-muted uppercase mb-1">Timezone</p>
              <p className="text-text-primary font-medium">Asia/Dubai (GMT+4)</p>
            </div>
            <div className="p-4 bg-background-secondary rounded-lg">
              <p className="text-xs text-text-muted uppercase mb-1">Refresh Interval</p>
              <p className="text-text-primary font-medium">15 minutes</p>
            </div>
            <div className="p-4 bg-background-secondary rounded-lg">
              <p className="text-xs text-text-muted uppercase mb-1">Cache TTL</p>
              <p className="text-text-primary font-medium">10 minutes</p>
            </div>
            <div className="p-4 bg-background-secondary rounded-lg">
              <p className="text-xs text-text-muted uppercase mb-1">Min Discount Threshold</p>
              <p className="text-text-primary font-medium">10%</p>
            </div>
          </div>
          
          <div className="p-4 bg-warning/10 border border-warning/30 rounded-lg flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-warning font-medium text-sm">Configuration Notice</p>
              <p className="text-text-secondary text-sm mt-1">
                Environment variables are managed through .env file. 
                Restart the application after making changes.
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardTitle>Quick Actions</CardTitle>
        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="btn-secondary justify-center">
            <Database className="w-4 h-4" />
            Init Schema
          </button>
          <button className="btn-secondary justify-center">
            <RefreshCw className="w-4 h-4" />
            Clear Cache
          </button>
          <button className="btn-secondary justify-center">
            <Settings className="w-4 h-4" />
            Reset Config
          </button>
          <button className="btn-secondary justify-center text-danger border-danger/30 hover:bg-danger/10">
            <XCircle className="w-4 h-4" />
            Purge Data
          </button>
        </div>
      </Card>
    </div>
  )
}
