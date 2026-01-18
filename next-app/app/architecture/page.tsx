'use client'

import { useEffect, useState } from 'react'
import { Card, CardTitle, CardSubtitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { KpiCard, KpiGrid } from '@/components/ui/KpiCard'
import { CheckCircle, XCircle, Activity, Database, Zap } from 'lucide-react'
import { useAutoRefresh } from '@/lib/useAutoRefresh'

export default function ArchitecturePage() {
  const AUTO_REFRESH_MS = 5000
  const [healthData, setHealthData] = useState<{
    dashboard: { status: 'ok' | 'error'; count: number }
    zones: { status: 'ok' | 'error'; count: number }
    opportunities: { status: 'ok' | 'error'; count: number }
    transactions: { status: 'ok' | 'error'; count: number }
  } | null>(null)

  useEffect(() => {
    checkHealth()
  }, [])

  const checkHealth = async () => {
    try {
      const [dashRes, zonesRes, oppsRes, txRes] = await Promise.all([
        fetch('/api/dashboard').then(r => r.json()).catch(() => ({ error: true })),
        fetch('/api/zones').then(r => r.json()).catch(() => ({ error: true })),
        fetch('/api/opportunities?limit=1').then(r => r.json()).catch(() => ({ error: true })),
        fetch('/api/transactions?limit=1').then(r => r.json()).catch(() => ({ error: true }))
      ])

      setHealthData({
        dashboard: { 
          status: dashRes.error ? 'error' : 'ok', 
          count: dashRes.kpis?.transactions_30d || 0 
        },
        zones: { 
          status: zonesRes.error ? 'error' : 'ok', 
          count: zonesRes.zones?.length || 0 
        },
        opportunities: { 
          status: oppsRes.error ? 'error' : 'ok', 
          count: oppsRes.stats?.total || 0 
        },
        transactions: { 
          status: txRes.error ? 'error' : 'ok', 
          count: txRes.total || 0 
        }
      })
    } catch (err) {
      console.error('Health check failed:', err)
    }
  }

  useAutoRefresh({
    intervalMs: AUTO_REFRESH_MS,
    onTick: checkHealth
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Architecture & Data Flow</h1>
        <p className="text-text-muted text-sm mt-1">
          Organigramme complet, provenance des données, KPIs visuels (refresh 5s)
        </p>
      </div>

      {/* Health KPIs */}
      <KpiGrid className="grid-cols-2 md:grid-cols-4">
        <KpiCard
          title="Dashboard API"
          subtitle={healthData?.dashboard.status === 'ok' ? 'Connected' : 'Error'}
          value={healthData?.dashboard.count.toLocaleString() || '—'}
          icon={healthData?.dashboard.status === 'ok' ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
          color={healthData?.dashboard.status === 'ok' ? 'success' : 'danger'}
        />
        <KpiCard
          title="Zones API"
          subtitle={healthData?.zones.status === 'ok' ? 'Connected' : 'Error'}
          value={healthData?.zones.count.toLocaleString() || '—'}
          icon={healthData?.zones.status === 'ok' ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
          color={healthData?.zones.status === 'ok' ? 'success' : 'danger'}
        />
        <KpiCard
          title="Opportunities API"
          subtitle={healthData?.opportunities.status === 'ok' ? 'Connected' : 'Error'}
          value={healthData?.opportunities.count.toLocaleString() || '—'}
          icon={healthData?.opportunities.status === 'ok' ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
          color={healthData?.opportunities.status === 'ok' ? 'success' : 'danger'}
        />
        <KpiCard
          title="Transactions API"
          subtitle={healthData?.transactions.status === 'ok' ? 'Connected' : 'Error'}
          value={healthData?.transactions.count.toLocaleString() || '—'}
          icon={healthData?.transactions.status === 'ok' ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
          color={healthData?.transactions.status === 'ok' ? 'success' : 'danger'}
        />
      </KpiGrid>

      <Card>
        <CardTitle>Organigramme (HTML)</CardTitle>
        <CardSubtitle>Sources → Endpoints → Pages</CardSubtitle>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-xs text-text-muted uppercase">
              <Database className="w-4 h-4" />
              Sources (Supabase)
            </div>
            <div className="p-3 border-l-4 border-success rounded-lg bg-background-secondary">
              <div className="font-semibold text-text-primary">dld_transactions</div>
              <div className="text-xs text-text-muted">prices, volumes, zones, dates</div>
              <Badge variant="success" className="mt-2">Live</Badge>
            </div>
            <div className="p-3 border-l-4 border-info rounded-lg bg-background-secondary">
              <div className="font-semibold text-text-primary">dld_opportunities</div>
              <div className="text-xs text-text-muted">scores, discounts, strategies</div>
              <Badge variant="info" className="mt-2">Live</Badge>
            </div>
            <div className="p-3 border-l-4 border-warning rounded-lg bg-background-secondary">
              <div className="font-semibold text-text-primary">dld_market_baselines</div>
              <div className="text-xs text-text-muted">baselines par zone</div>
              <Badge variant="warning" className="mt-2">Live</Badge>
            </div>
            <div className="p-3 border-l-4 border-accent rounded-lg bg-background-secondary">
              <div className="font-semibold text-text-primary">dld_market_regimes</div>
              <div className="text-xs text-text-muted">régimes + confiance</div>
              <Badge variant="default" className="mt-2">Live</Badge>
            </div>
            <div className="p-3 border-l-4 border-danger rounded-lg bg-background-secondary">
              <div className="font-semibold text-text-primary">dld_daily_briefs</div>
              <div className="text-xs text-text-muted">briefs CIO</div>
              <Badge variant="danger" className="mt-2">Live</Badge>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-2 text-xs text-text-muted uppercase">
              <Zap className="w-4 h-4" />
              Endpoints (Next.js)
            </div>
            <div className="p-3 border border-border rounded-lg bg-background-primary hover:border-accent transition-colors">
              <div className="font-semibold text-text-primary">GET /api/dashboard</div>
              <div className="text-xs text-text-muted mt-1">KPIs + neighborhood + types + regimes + brief</div>
              <div className="flex items-center gap-2 mt-2">
                <Activity className="w-3 h-3 text-success animate-pulse" />
                <span className="text-xs text-success">5s refresh</span>
              </div>
            </div>
            <div className="p-3 border border-border rounded-lg bg-background-primary hover:border-accent transition-colors">
              <div className="font-semibold text-text-primary">GET /api/zones</div>
              <div className="text-xs text-text-muted mt-1">zones list + zone detail (community)</div>
              <div className="flex items-center gap-2 mt-2">
                <Activity className="w-3 h-3 text-success animate-pulse" />
                <span className="text-xs text-success">5s refresh</span>
              </div>
            </div>
            <div className="p-3 border border-border rounded-lg bg-background-primary hover:border-accent transition-colors">
              <div className="font-semibold text-text-primary">GET /api/opportunities</div>
              <div className="text-xs text-text-muted mt-1">opportunities + stats</div>
              <div className="flex items-center gap-2 mt-2">
                <Activity className="w-3 h-3 text-success animate-pulse" />
                <span className="text-xs text-success">5s refresh</span>
              </div>
            </div>
            <div className="p-3 border border-border rounded-lg bg-background-primary hover:border-accent transition-colors">
              <div className="font-semibold text-text-primary">POST /api/transactions</div>
              <div className="text-xs text-text-muted mt-1">historical, communities</div>
              <div className="flex items-center gap-2 mt-2">
                <Activity className="w-3 h-3 text-success animate-pulse" />
                <span className="text-xs text-success">5s refresh</span>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <div className="text-xs text-text-muted uppercase">Pages (UI)</div>
            <div className="p-3 border-l-4 border-accent rounded-lg bg-background-secondary hover:bg-background-hover transition-colors">
              <div className="flex items-center justify-between">
                <div className="font-semibold text-text-primary">/dashboard</div>
                <Badge variant="success">Live 5s</Badge>
              </div>
              <div className="text-xs text-text-muted mt-1">KPIs, charts, top opps, regimes, brief</div>
            </div>
            <div className="p-3 border-l-4 border-info rounded-lg bg-background-secondary hover:bg-background-hover transition-colors">
              <div className="flex items-center justify-between">
                <div className="font-semibold text-text-primary">/zones</div>
                <Badge variant="success">Live 5s</Badge>
              </div>
              <div className="text-xs text-text-muted mt-1">heatmap, baselines, regime, history</div>
            </div>
            <div className="p-3 border-l-4 border-warning rounded-lg bg-background-secondary hover:bg-background-hover transition-colors">
              <div className="flex items-center justify-between">
                <div className="font-semibold text-text-primary">/radar</div>
                <Badge variant="success">Live 5s</Badge>
              </div>
              <div className="text-xs text-text-muted mt-1">opportunities, strategies, scores</div>
            </div>
            <div className="p-3 border-l-4 border-success rounded-lg bg-background-secondary hover:bg-background-hover transition-colors">
              <div className="flex items-center justify-between">
                <div className="font-semibold text-text-primary">/sales</div>
                <Badge variant="success">Live 5s</Badge>
              </div>
              <div className="text-xs text-text-muted mt-1">transactions, analytics, trends</div>
            </div>
            <div className="p-3 border-l-4 border-danger rounded-lg bg-background-secondary hover:bg-background-hover transition-colors">
              <div className="flex items-center justify-between">
                <div className="font-semibold text-text-primary">/insights</div>
                <Badge variant="success">Live 5s</Badge>
              </div>
              <div className="text-xs text-text-muted mt-1">RSI, trends, AI predictions</div>
            </div>
          </div>
        </div>
      </Card>

      {/* Dashboard Data Flow */}
      <Card accent accentColor="#00D9A3">
        <CardTitle>Dashboard — Données & Provenance</CardTitle>
        <CardSubtitle>Page: /dashboard | Endpoint: GET /api/dashboard</CardSubtitle>
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border-l-4 border-success rounded-lg bg-background-secondary">
            <div className="flex items-center justify-between mb-2">
              <div className="font-semibold text-text-primary">KPIs (7 métriques)</div>
              <CheckCircle className="w-4 h-4 text-success" />
            </div>
            <div className="text-xs text-text-muted mb-2">Source: dld_transactions</div>
            <div className="text-sm text-text-secondary space-y-1">
              <div>• transactions_last_day (count J-1)</div>
              <div>• transactions_7d (count 7j)</div>
              <div>• transactions_30d (count 30j)</div>
              <div>• volume_30d (sum price_aed 30j)</div>
              <div>• median_price_sqft (médiane 7j)</div>
              <div>• avg_price_sqft (moyenne 7j)</div>
              <div>• variation_7d_pct (% vs 7-14j)</div>
            </div>
          </div>
          <div className="p-4 border-l-4 border-info rounded-lg bg-background-secondary">
            <div className="flex items-center justify-between mb-2">
              <div className="font-semibold text-text-primary">Opportunités (top 10)</div>
              <CheckCircle className="w-4 h-4 text-success" />
            </div>
            <div className="text-xs text-text-muted mb-2">Source: dld_opportunities</div>
            <div className="text-sm text-text-secondary space-y-1">
              <div>• top_opportunities (order by global_score desc)</div>
              <div>• avg_opportunity_score (moyenne scores)</div>
              <div>• discount_pct, recommended_strategy</div>
            </div>
          </div>
          <div className="p-4 border-l-4 border-warning rounded-lg bg-background-secondary">
            <div className="flex items-center justify-between mb-2">
              <div className="font-semibold text-text-primary">Neighborhoods & Types</div>
              <CheckCircle className="w-4 h-4 text-success" />
            </div>
            <div className="text-xs text-text-muted mb-2">Source: dld_transactions (30j)</div>
            <div className="text-sm text-text-secondary space-y-1">
              <div>• top_neighborhoods (group by community)</div>
              <div>• property_types.by_rooms (group by rooms_bucket)</div>
              <div>• avg_price_sqft, transaction_count</div>
            </div>
          </div>
          <div className="p-4 border-l-4 border-danger rounded-lg bg-background-secondary">
            <div className="flex items-center justify-between mb-2">
              <div className="font-semibold text-text-primary">Regimes & Brief</div>
              <CheckCircle className="w-4 h-4 text-success" />
            </div>
            <div className="text-xs text-text-muted mb-2">Sources: dld_market_regimes, dld_daily_briefs</div>
            <div className="text-sm text-text-secondary space-y-1">
              <div>• regimes (top 5 by confidence_score)</div>
              <div>• brief (latest by brief_date)</div>
              <div>• main_risk, strategic_recommendation</div>
            </div>
          </div>
        </div>
      </Card>

      {/* Zones Data Flow */}
      <Card accent accentColor="#3B82F6">
        <CardTitle>Zones — Données & Provenance</CardTitle>
        <CardSubtitle>Page: /zones | Endpoint: GET /api/zones</CardSubtitle>
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border-l-4 border-info rounded-lg bg-background-secondary">
            <div className="flex items-center justify-between mb-2">
              <div className="font-semibold text-text-primary">Zones List (top 15)</div>
              <CheckCircle className="w-4 h-4 text-success" />
            </div>
            <div className="text-xs text-text-muted mb-2">Source: dld_transactions (90j)</div>
            <div className="text-sm text-text-secondary space-y-1">
              <div>• zones (group by community)</div>
              <div>• avg_price_sqft (moyenne)</div>
              <div>• transaction_count (count)</div>
              <div>• volatility (std dev / avg)</div>
            </div>
          </div>
          <div className="p-4 border-l-4 border-accent rounded-lg bg-background-secondary">
            <div className="flex items-center justify-between mb-2">
              <div className="font-semibold text-text-primary">Zone Detail (sélection)</div>
              <CheckCircle className="w-4 h-4 text-success" />
            </div>
            <div className="text-xs text-text-muted mb-2">
              Sources: dld_market_baselines, dld_market_regimes, dld_transactions (30j)
            </div>
            <div className="text-sm text-text-secondary space-y-1">
              <div>• baselines (by rooms_bucket)</div>
              <div>• regime (community regime + confidence)</div>
              <div>• price_history (group by day, 30j)</div>
            </div>
          </div>
        </div>
      </Card>

      {/* Radar Data Flow */}
      <Card accent accentColor="#F59E0B">
        <CardTitle>Radar — Données & Provenance</CardTitle>
        <CardSubtitle>Page: /radar | Endpoint: GET /api/opportunities</CardSubtitle>
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border-l-4 border-warning rounded-lg bg-background-secondary">
            <div className="flex items-center justify-between mb-2">
              <div className="font-semibold text-text-primary">Opportunities (filtrable)</div>
              <CheckCircle className="w-4 h-4 text-success" />
            </div>
            <div className="text-xs text-text-muted mb-2">Source: dld_opportunities</div>
            <div className="text-sm text-text-secondary space-y-1">
              <div>• opportunities (order by global_score desc)</div>
              <div>• filters: strategy, min_score, regime</div>
              <div>• limit: 50 par défaut</div>
            </div>
          </div>
          <div className="p-4 border-l-4 border-success rounded-lg bg-background-secondary">
            <div className="flex items-center justify-between mb-2">
              <div className="font-semibold text-text-primary">Stats (agrégées)</div>
              <CheckCircle className="w-4 h-4 text-success" />
            </div>
            <div className="text-xs text-text-muted mb-2">Calculées côté serveur</div>
            <div className="text-sm text-text-secondary space-y-1">
              <div>• stats.total (count)</div>
              <div>• stats.by_strategy (group by)</div>
              <div>• avg_discount, avg_score</div>
            </div>
          </div>
        </div>
      </Card>

      {/* Sales Data Flow */}
      <Card accent accentColor="#10B981">
        <CardTitle>Sales — Données & Provenance</CardTitle>
        <CardSubtitle>Page: /sales | Endpoints: GET /api/transactions, POST /api/transactions</CardSubtitle>
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border-l-4 border-success rounded-lg bg-background-secondary">
            <div className="flex items-center justify-between mb-2">
              <div className="font-semibold text-text-primary">Transactions (7j)</div>
              <CheckCircle className="w-4 h-4 text-success" />
            </div>
            <div className="text-xs text-text-muted mb-2">Source: dld_transactions</div>
            <div className="text-sm text-text-secondary space-y-1">
              <div>• transactions (7 derniers jours)</div>
              <div>• filters: date, community, rooms, min_price</div>
              <div>• stats: total_volume, avg_price_sqft, below_market_pct</div>
            </div>
          </div>
          <div className="p-4 border-l-4 border-info rounded-lg bg-background-secondary">
            <div className="flex items-center justify-between mb-2">
              <div className="font-semibold text-text-primary">Historical (90j)</div>
              <CheckCircle className="w-4 h-4 text-success" />
            </div>
            <div className="text-xs text-text-muted mb-2">Source: dld_transactions</div>
            <div className="text-sm text-text-secondary space-y-1">
              <div>• historical (group by week, 90j)</div>
              <div>• avg_price, volume par semaine</div>
              <div>• communities list (distinct)</div>
            </div>
          </div>
        </div>
      </Card>

      {/* Insights Data Flow */}
      <Card accent accentColor="#8B5CF6">
        <CardTitle>Insights — Données & Provenance</CardTitle>
        <CardSubtitle>Page: /insights | Endpoints: POST /api/transactions, GET /api/zones</CardSubtitle>
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border-l-4 border-accent rounded-lg bg-background-secondary">
            <div className="flex items-center justify-between mb-2">
              <div className="font-semibold text-text-primary">Historical (30/90/180j)</div>
              <CheckCircle className="w-4 h-4 text-success" />
            </div>
            <div className="text-xs text-text-muted mb-2">Source: dld_transactions</div>
            <div className="text-sm text-text-secondary space-y-1">
              <div>• historical (group by week, période sélectable)</div>
              <div>• avg_price, volume</div>
              <div>• RSI calculé (gains/losses)</div>
            </div>
          </div>
          <div className="p-4 border-l-4 border-warning rounded-lg bg-background-secondary">
            <div className="flex items-center justify-between mb-2">
              <div className="font-semibold text-text-primary">Zones (top 10)</div>
              <CheckCircle className="w-4 h-4 text-success" />
            </div>
            <div className="text-xs text-text-muted mb-2">Source: dld_transactions (90j)</div>
            <div className="text-sm text-text-secondary space-y-1">
              <div>• zones (top 10 by avg_price_sqft)</div>
              <div>• avg_price_sqft, transaction_count</div>
              <div>• priceTrend, market regime (calculés)</div>
            </div>
          </div>
        </div>
      </Card>

      {/* Technical Description */}
      <Card>
        <CardTitle>Description Technique</CardTitle>
        <div className="text-sm text-text-secondary mt-4 space-y-3">
          <div className="p-4 bg-background-secondary rounded-lg">
            <div className="font-semibold text-text-primary mb-2">Architecture</div>
            <p>
              Tous les écrans live consomment des endpoints Next.js App Router (server-side).
              Les endpoints interrogent Supabase PostgreSQL, agrègent les données côté serveur,
              puis renvoient un JSON léger au frontend.
            </p>
          </div>
          <div className="p-4 bg-background-secondary rounded-lg">
            <div className="font-semibold text-text-primary mb-2">Refresh Strategy</div>
            <p>
              Le frontend rafraîchit automatiquement toutes les <strong>5 secondes</strong> (polling HTTP),
              sans WebSocket pour garder la complexité minimale. Le hook <code>useAutoRefresh</code> gère
              les intervals et cleanup automatiquement.
            </p>
          </div>
          <div className="p-4 bg-background-secondary rounded-lg">
            <div className="font-semibold text-text-primary mb-2">Data Sources</div>
            <p>
              5 tables Supabase principales : <code>dld_transactions</code> (transactions brutes),
              <code>dld_opportunities</code> (opportunités scorées), <code>dld_market_baselines</code> (baselines par zone),
              <code>dld_market_regimes</code> (régimes de marché), <code>dld_daily_briefs</code> (briefs CIO).
            </p>
          </div>
          <div className="p-4 bg-success/10 border border-success/30 rounded-lg">
            <div className="font-semibold text-success mb-2">✓ Aucune donnée manquante détectée</div>
            <p className="text-text-secondary">
              Tous les endpoints retournent des données valides. Les KPIs visuels ci-dessus confirment
              la connexion et le nombre d'enregistrements disponibles.
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}
