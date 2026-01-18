'use client'

import { cn } from '@/lib/utils'

interface GaugeChartProps {
  value: number
  min?: number
  max?: number
  label?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function GaugeChart({
  value,
  min = 0,
  max = 100,
  label,
  size = 'md',
  className,
}: GaugeChartProps) {
  const percentage = Math.min(Math.max((value - min) / (max - min) * 100, 0), 100)
  
  // Calculate color based on value
  const getColor = (pct: number) => {
    if (pct >= 70) return '#10B981' // success
    if (pct >= 40) return '#F59E0B' // warning
    return '#EF4444' // danger
  }

  const color = getColor(percentage)
  
  const sizeClasses = {
    sm: { container: 'w-24 h-12', text: 'text-lg', label: 'text-[10px]' },
    md: { container: 'w-32 h-16', text: 'text-2xl', label: 'text-xs' },
    lg: { container: 'w-40 h-20', text: 'text-3xl', label: 'text-sm' },
  }

  // SVG arc calculation
  const strokeWidth = size === 'sm' ? 6 : size === 'md' ? 8 : 10
  const radius = 50 - strokeWidth / 2
  const circumference = Math.PI * radius
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  return (
    <div className={cn("relative flex flex-col items-center", className)}>
      <div className={cn("relative", sizeClasses[size].container)}>
        <svg viewBox="0 0 100 60" className="w-full h-full overflow-visible">
          {/* Background arc */}
          <path
            d={`M ${strokeWidth / 2} 50 A ${radius} ${radius} 0 0 1 ${100 - strokeWidth / 2} 50`}
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
          {/* Value arc */}
          <path
            d={`M ${strokeWidth / 2} 50 A ${radius} ${radius} 0 0 1 ${100 - strokeWidth / 2} 50`}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{ transition: 'stroke-dashoffset 0.5s ease-out' }}
          />
        </svg>
        
        {/* Value display */}
        <div className="absolute inset-0 flex items-end justify-center pb-1">
          <span className={cn("font-bold text-text-primary", sizeClasses[size].text)}>
            {Math.round(value)}
          </span>
          <span className="text-text-muted text-xs ml-0.5 mb-1">%</span>
        </div>
      </div>
      
      {label && (
        <span className={cn("text-text-muted mt-1", sizeClasses[size].label)}>
          {label}
        </span>
      )}
    </div>
  )
}
