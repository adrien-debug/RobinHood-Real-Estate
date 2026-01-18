'use client'

import { cn } from '@/lib/utils'

interface LiveIndicatorProps {
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

export function LiveIndicator({ className, size = 'sm' }: LiveIndicatorProps) {
  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4'
  }

  return (
    <div className={cn('relative flex items-center justify-center', className)}>
      {/* Pulsing outer ring */}
      <div className={cn(
        'absolute rounded-full bg-success animate-ping opacity-75',
        sizeClasses[size]
      )} />
      {/* Solid inner dot */}
      <div className={cn(
        'relative rounded-full bg-success',
        sizeClasses[size]
      )} />
    </div>
  )
}
