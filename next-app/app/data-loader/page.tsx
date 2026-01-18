'use client'

import { useState, useEffect } from 'react'
import { RefreshCw, Database, CheckCircle2, XCircle, TrendingUp, Building2, MapPin } from 'lucide-react'
import { useAutoRefresh } from '@/lib/useAutoRefresh'

export default function DataLoaderPage() {
  const AUTO_REFRESH_MS = 5000
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState<any>(null)
  const [loadResult, setLoadResult] = useState<any>(null)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/load-data')
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const loadData = async () => {
    setLoading(true)
    setLoadResult(null)

    try {
      const response = await fetch('/api/load-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'load_transactions' })
      })

      const result = await response.json()
      setLoadResult(result)

      if (result.success) {
        // Rafraîchir les stats
        setTimeout(fetchStats, 1000)
      }
    } catch (error: any) {
      setLoadResult({ error: error.message })
    } finally {
      setLoading(false)
    }
  }

  useAutoRefresh({
    intervalMs: AUTO_REFRESH_MS,
    onTick: fetchStats,
    enabled: !loading
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Data Loader</h1>
          <p className="text-text-secondary mt-1">
            Charger les données historiques dans Supabase
          </p>
        </div>
        <button
          onClick={loadData}
          disabled={loading}
          className="flex items-center gap-2 px-6 py-3 bg-accent text-background-primary rounded-lg hover:bg-accent/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          {loading ? 'Chargement...' : 'Charger les données'}
        </button>
      </div>

      {/* Load Result */}
      {loadResult && (
        <div className={`p-6 rounded-lg border ${
          loadResult.error 
            ? 'bg-danger/10 border-danger' 
            : 'bg-success/10 border-success'
        }`}>
          <div className="flex items-start gap-3">
            {loadResult.error ? (
              <XCircle className="w-6 h-6 text-danger flex-shrink-0 mt-1" />
            ) : (
              <CheckCircle2 className="w-6 h-6 text-success flex-shrink-0 mt-1" />
            )}
            <div className="flex-1">
              <h3 className={`font-semibold mb-2 ${
                loadResult.error ? 'text-danger' : 'text-success'
              }`}>
                {loadResult.error ? 'Erreur' : 'Succès'}
              </h3>
              {loadResult.error ? (
                <p className="text-text-secondary">{loadResult.error}</p>
              ) : (
                <div className="space-y-2 text-text-secondary">
                  <p>Total enregistrements: <span className="font-semibold text-text-primary">{loadResult.totalRecords?.toLocaleString()}</span></p>
                  <p>Insérés: <span className="font-semibold text-success">{loadResult.inserted?.toLocaleString()}</span></p>
                  {loadResult.errors > 0 && (
                    <p>Erreurs: <span className="font-semibold text-danger">{loadResult.errors?.toLocaleString()}</span></p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Current Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Total Transactions */}
          <div className="bg-background-secondary p-6 rounded-lg border border-border">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 bg-accent/20 rounded-lg">
                <Database className="w-6 h-6 text-accent" />
              </div>
              <div>
                <p className="text-text-muted text-sm">Total Transactions</p>
                <p className="text-2xl font-bold text-text-primary">
                  {stats.count?.toLocaleString() || 0}
                </p>
              </div>
            </div>
          </div>

          {/* Avg Price */}
          <div className="bg-background-secondary p-6 rounded-lg border border-border">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 bg-success/20 rounded-lg">
                <TrendingUp className="w-6 h-6 text-success" />
              </div>
              <div>
                <p className="text-text-muted text-sm">Prix Moyen</p>
                <p className="text-2xl font-bold text-text-primary">
                  {stats.avgPrice ? `${(stats.avgPrice / 1000000).toFixed(1)}M` : '0'} AED
                </p>
              </div>
            </div>
          </div>

          {/* Avg Area */}
          <div className="bg-background-secondary p-6 rounded-lg border border-border">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 bg-warning/20 rounded-lg">
                <Building2 className="w-6 h-6 text-warning" />
              </div>
              <div>
                <p className="text-text-muted text-sm">Superficie Moy</p>
                <p className="text-2xl font-bold text-text-primary">
                  {stats.avgArea ? Math.round(stats.avgArea).toLocaleString() : '0'} sqft
                </p>
              </div>
            </div>
          </div>

          {/* Top Community */}
          <div className="bg-background-secondary p-6 rounded-lg border border-border">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 bg-info/20 rounded-lg">
                <MapPin className="w-6 h-6 text-info" />
              </div>
              <div>
                <p className="text-text-muted text-sm">Top Communauté</p>
                <p className="text-lg font-bold text-text-primary truncate">
                  {stats.topCommunities?.[0]?.community || 'N/A'}
                </p>
                <p className="text-sm text-text-muted">
                  {stats.topCommunities?.[0]?.count?.toLocaleString() || 0} tx
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Top Types */}
      {stats?.topTypes && (
        <div className="bg-background-secondary p-6 rounded-lg border border-border">
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            Par Type de Propriété
          </h3>
          <div className="space-y-3">
            {stats.topTypes.map((item: any, index: number) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-text-secondary capitalize">{item.type}</span>
                <div className="flex items-center gap-3">
                  <div className="w-32 h-2 bg-background-primary rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-accent"
                      style={{ 
                        width: `${(item.count / stats.count) * 100}%` 
                      }}
                    />
                  </div>
                  <span className="text-text-primary font-semibold w-16 text-right">
                    {item.count.toLocaleString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Communities */}
      {stats?.topCommunities && (
        <div className="bg-background-secondary p-6 rounded-lg border border-border">
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            Top 10 Communautés
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {stats.topCommunities.map((item: any, index: number) => (
              <div 
                key={index}
                className="flex items-center justify-between p-3 bg-background-primary rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <span className="text-text-muted font-mono text-sm">
                    #{index + 1}
                  </span>
                  <span className="text-text-primary">{item.community}</span>
                </div>
                <span className="text-accent font-semibold">
                  {item.count.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Samples */}
      {stats?.samples && stats.samples.length > 0 && (
        <div className="bg-background-secondary p-6 rounded-lg border border-border">
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            Transactions Récentes
          </h3>
          <div className="space-y-3">
            {stats.samples.map((tx: any, index: number) => (
              <div 
                key={index}
                className="p-4 bg-background-primary rounded-lg border border-border"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-semibold text-text-primary">{tx.community}</p>
                    <p className="text-sm text-text-muted capitalize">
                      {tx.property_type} • {tx.rooms_bucket || 'N/A'}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-accent">
                      {tx.price_aed?.toLocaleString()} AED
                    </p>
                    {tx.price_per_sqft && (
                      <p className="text-sm text-text-muted">
                        {tx.price_per_sqft.toLocaleString()} AED/sqft
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-4 text-xs text-text-muted">
                  <span>{tx.transaction_date}</span>
                  {tx.area_sqft && <span>{tx.area_sqft.toLocaleString()} sqft</span>}
                  {tx.is_offplan && (
                    <span className="px-2 py-1 bg-warning/20 text-warning rounded">
                      Offplan
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
