'use client'

import { Bell, RefreshCw, Calendar } from 'lucide-react'
import { useState, useEffect } from 'react'
import { formatDate } from '@/lib/utils'

export function Header() {
  const [currentTime, setCurrentTime] = useState<Date | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)

  useEffect(() => {
    setCurrentTime(new Date())
    const interval = setInterval(() => {
      setCurrentTime(new Date())
    }, 60000)
    return () => clearInterval(interval)
  }, [])

  const handleRefresh = () => {
    setIsRefreshing(true)
    window.location.reload()
  }

  return (
    <header className="h-16 bg-background-secondary border-b border-border px-6 flex items-center justify-between">
      {/* Left side */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-text-secondary">
          <Calendar className="w-4 h-4" />
          <span className="text-sm">
            {currentTime ? formatDate(currentTime) : 'Loading...'}
          </span>
        </div>
        <div className="h-4 w-px bg-border" />
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
          <span className="text-sm text-text-muted">Live</span>
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3">
        {/* Refresh button */}
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-background-hover transition-colors"
        >
          <RefreshCw className={`w-5 h-5 ${isRefreshing ? 'animate-spin' : ''}`} />
        </button>

        {/* Notifications */}
        <button className="relative p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-background-hover transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-danger" />
        </button>

        {/* Timezone */}
        <div className="px-3 py-1.5 rounded-lg bg-background-card border border-border text-xs text-text-muted">
          Dubai (GMT+4)
        </div>
      </div>
    </header>
  )
}
