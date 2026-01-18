'use client'

import { cn } from '@/lib/utils'

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function Loading({ size = 'md', className }: LoadingProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }

  return (
    <div className={cn("flex items-center justify-center", className)}>
      <div
        className={cn(
          "animate-spin rounded-full border-2 border-border border-t-accent",
          sizeClasses[size]
        )}
      />
    </div>
  )
}

export function LoadingPage() {
  return (
    <div className="flex-1 flex items-center justify-center min-h-[400px]">
      <div className="text-center">
        <Loading size="lg" />
        <p className="mt-4 text-text-muted">Loading data...</p>
      </div>
    </div>
  )
}

export function LoadingCard() {
  return (
    <div className="card animate-pulse">
      <div className="h-4 bg-background-hover rounded w-1/3 mb-4" />
      <div className="h-8 bg-background-hover rounded w-1/2 mb-2" />
      <div className="h-4 bg-background-hover rounded w-1/4" />
    </div>
  )
}
