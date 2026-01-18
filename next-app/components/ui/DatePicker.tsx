'use client'

import { cn } from '@/lib/utils'
import { Calendar } from 'lucide-react'

interface DatePickerProps {
  value: string
  onChange: (value: string) => void
  max?: string
  min?: string
  className?: string
  disabled?: boolean
}

export function DatePicker({ 
  value, 
  onChange, 
  max,
  min,
  className,
  disabled = false
}: DatePickerProps) {
  return (
    <div className={cn("relative", className)}>
      <input
        type="date"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        max={max}
        min={min}
        disabled={disabled}
        className={cn(
          "w-full px-3 py-2 pl-10 bg-background-secondary border border-border rounded-lg",
          "text-text-primary text-sm",
          "focus:outline-none focus:border-accent",
          "transition-colors cursor-pointer",
          disabled && "opacity-50 cursor-not-allowed",
          // Dark theme date input styling
          "[color-scheme:dark]"
        )}
      />
      <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted pointer-events-none" />
    </div>
  )
}
