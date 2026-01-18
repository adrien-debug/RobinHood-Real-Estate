'use client'

import { cn } from '@/lib/utils'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface KpiCardProps {
  title: string
  subtitle?: string
  value: string | number
  trend?: number
  color?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'accent'
  icon?: React.ReactNode
  className?: string
}

export function KpiCard({ 
  title, 
  subtitle, 
  value, 
  trend, 
  color = 'default',
  icon,
  className 
}: KpiCardProps) {
  const colorClasses = {
    default: 'border-border',
    success: 'border-l-success border-l-4',
    warning: 'border-l-warning border-l-4',
    danger: 'border-l-danger border-l-4',
    info: 'border-l-info border-l-4',
    accent: 'border-l-accent border-l-4',
  }

  const valueColorClasses = {
    default: 'text-text-primary',
    success: 'text-success',
    warning: 'text-warning',
    danger: 'text-danger',
    info: 'text-info',
    accent: 'text-accent',
  }

  const TrendIcon = trend && trend > 0 ? TrendingUp : trend && trend < 0 ? TrendingDown : Minus

  return (
    <div className={cn(
      "kpi-card flex flex-col justify-between min-h-[100px]",
      colorClasses[color],
      className
    )}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-text-muted uppercase tracking-wider">
            {title}
          </p>
          {subtitle && (
            <p className="text-[10px] text-text-disabled mt-0.5">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className="text-text-muted">{icon}</div>
        )}
      </div>
      
      <div className="mt-2">
        <p className={cn(
          "text-2xl font-bold",
          valueColorClasses[color]
        )}>
          {value}
        </p>
        
        {trend !== undefined && (
          <div className={cn(
            "flex items-center gap-1 mt-1 text-xs font-medium",
            trend > 0 ? "text-success" : trend < 0 ? "text-danger" : "text-text-muted"
          )}>
            <TrendIcon className="w-3 h-3" />
            <span>{trend > 0 ? '+' : ''}{trend.toFixed(1)}%</span>
          </div>
        )}
      </div>
    </div>
  )
}

// Grid wrapper for KPI cards
export function KpiGrid({ children, className }: { children: React.ReactNode, className?: string }) {
  return (
    <div className={cn(
      "grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4",
      className
    )}>
      {children}
    </div>
  )
}
