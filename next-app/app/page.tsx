'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Building2, TrendingUp, Target, BarChart3, Bell, CheckCircle2, Zap } from 'lucide-react'
import { supabase } from '@/lib/supabase'

export default function HomePage() {
  const router = useRouter()
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'error'>('checking')
  const [dataCount, setDataCount] = useState(0)

  useEffect(() => {
    // Check Supabase connection
    const checkConnection = async () => {
      try {
        const { count, error } = await supabase
          .from('dld_transactions')
          .select('*', { count: 'exact', head: true })
        
        if (error) throw error
        
        setApiStatus('connected')
        setDataCount(count || 0)
      } catch (error) {
        console.error('Connection error:', error)
        setApiStatus('error')
      }
    }

    checkConnection()

    // Auto-redirect to dashboard after 3 seconds
    const timer = setTimeout(() => {
      router.push('/dashboard')
    }, 3000)

    return () => clearTimeout(timer)
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background-primary via-background-secondary to-background-primary">
      <div className="text-center space-y-8 p-8">
        {/* Logo with Status LED */}
        <div className="flex justify-center mb-8">
          <div className="relative">
            <div className="w-24 h-24 bg-accent rounded-full flex items-center justify-center shadow-2xl">
              <Building2 className="w-12 h-12 text-background-primary" />
            </div>
            {/* LED Status Indicator */}
            <div className={`absolute -top-2 -right-2 w-8 h-8 rounded-full flex items-center justify-center shadow-lg ${
              apiStatus === 'connected' ? 'bg-success animate-pulse' :
              apiStatus === 'checking' ? 'bg-warning animate-pulse' :
              'bg-danger'
            }`}>
              {apiStatus === 'connected' ? (
                <CheckCircle2 className="w-4 h-4 text-background-primary" />
              ) : (
                <Zap className="w-4 h-4 text-background-primary" />
              )}
            </div>
          </div>
        </div>

        {/* Title */}
        <div>
          <h1 className="text-5xl font-bold text-text-primary mb-2">
            Robin
          </h1>
          <p className="text-xl text-accent font-semibold">
            Dubai Real Estate Intelligence
          </p>
          <p className="text-text-muted mt-2">
            Institutional-grade market intelligence
          </p>
        </div>

        {/* API Status */}
        <div className="mt-6">
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${
            apiStatus === 'connected' ? 'bg-success/20 text-success' :
            apiStatus === 'checking' ? 'bg-warning/20 text-warning' :
            'bg-danger/20 text-danger'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              apiStatus === 'connected' ? 'bg-success' :
              apiStatus === 'checking' ? 'bg-warning animate-pulse' :
              'bg-danger'
            }`}></div>
            <span className="text-sm font-medium">
              {apiStatus === 'connected' ? `✓ Live Data Connected (${dataCount.toLocaleString()} transactions)` :
               apiStatus === 'checking' ? 'Checking API connection...' :
               '✗ Connection Error'}
            </span>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-12 max-w-2xl mx-auto">
          <div className="bg-background-secondary p-4 rounded-lg border border-border hover:border-accent transition-colors">
            <TrendingUp className="w-6 h-6 text-accent mx-auto mb-2" />
            <p className="text-xs text-text-secondary">Real-time Data</p>
          </div>
          <div className="bg-background-secondary p-4 rounded-lg border border-border hover:border-accent transition-colors">
            <Target className="w-6 h-6 text-accent mx-auto mb-2" />
            <p className="text-xs text-text-secondary">Smart Scoring</p>
          </div>
          <div className="bg-background-secondary p-4 rounded-lg border border-border hover:border-accent transition-colors">
            <BarChart3 className="w-6 h-6 text-accent mx-auto mb-2" />
            <p className="text-xs text-text-secondary">Market Regimes</p>
          </div>
          <div className="bg-background-secondary p-4 rounded-lg border border-border hover:border-accent transition-colors">
            <Bell className="w-6 h-6 text-accent mx-auto mb-2" />
            <p className="text-xs text-text-secondary">Live Alerts</p>
          </div>
        </div>

        {/* Loading indicator */}
        <div className="mt-8">
          <div className="inline-flex items-center gap-2 text-text-muted">
            <div className="w-2 h-2 bg-accent rounded-full animate-ping"></div>
            <span className="text-sm">Loading dashboard...</span>
          </div>
        </div>
      </div>
    </div>
  )
}
