'use client'

import { cn } from '@/lib/utils'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'accent' | 'outline'
  size?: 'sm' | 'md'
  className?: string
}

export function Badge({ 
  children, 
  variant = 'default', 
  size = 'sm',
  className 
}: BadgeProps) {
  const variantClasses = {
    default: 'bg-background-hover text-text-secondary',
    success: 'bg-success/20 text-success',
    warning: 'bg-warning/20 text-warning',
    danger: 'bg-danger/20 text-danger',
    info: 'bg-info/20 text-info',
    accent: 'bg-accent/20 text-accent',
    outline: 'bg-transparent border border-border text-text-secondary',
  }

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
  }

  return (
    <span className={cn(
      "inline-flex items-center font-semibold rounded-md",
      variantClasses[variant],
      sizeClasses[size],
      className
    )}>
      {children}
    </span>
  )
}

// Regime-specific badges
export function RegimeBadge({ regime }: { regime: string }) {
  const variants: Record<string, 'success' | 'info' | 'warning' | 'danger' | 'default'> = {
    ACCUMULATION: 'success',
    EXPANSION: 'info',
    DISTRIBUTION: 'warning',
    RETOURNEMENT: 'danger',
    NEUTRAL: 'default',
  }
  
  return (
    <Badge variant={variants[regime] || 'default'}>
      {regime}
    </Badge>
  )
}

// Strategy-specific badges
export function StrategyBadge({ strategy }: { strategy: string }) {
  const variants: Record<string, 'success' | 'info' | 'accent' | 'default'> = {
    FLIP: 'success',
    RENT: 'info',
    LONG: 'accent',
    IGNORE: 'default',
  }
  
  return (
    <Badge variant={variants[strategy] || 'default'}>
      {strategy}
    </Badge>
  )
}
