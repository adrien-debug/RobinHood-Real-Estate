'use client'

import { cn } from '@/lib/utils'

interface CardProps {
  children: React.ReactNode
  className?: string
  accent?: boolean
  accentColor?: string
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

export function Card({ 
  children, 
  className, 
  accent = false,
  accentColor,
  padding = 'md'
}: CardProps) {
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  }

  return (
    <div 
      className={cn(
        "bg-background-card rounded-xl border border-border transition-all duration-200",
        accent && "border-l-4",
        paddingClasses[padding],
        className
      )}
      style={accent && accentColor ? { borderLeftColor: accentColor } : undefined}
    >
      {children}
    </div>
  )
}

export function CardHeader({ children, className }: { children: React.ReactNode, className?: string }) {
  return (
    <div className={cn("mb-4", className)}>
      {children}
    </div>
  )
}

export function CardTitle({ children, className }: { children: React.ReactNode, className?: string }) {
  return (
    <h3 className={cn("text-lg font-semibold text-text-primary", className)}>
      {children}
    </h3>
  )
}

export function CardSubtitle({ children, className }: { children: React.ReactNode, className?: string }) {
  return (
    <p className={cn("text-xs font-semibold text-text-muted uppercase tracking-wider mt-1", className)}>
      {children}
    </p>
  )
}

export function CardContent({ children, className }: { children: React.ReactNode, className?: string }) {
  return (
    <div className={cn("", className)}>
      {children}
    </div>
  )
}
