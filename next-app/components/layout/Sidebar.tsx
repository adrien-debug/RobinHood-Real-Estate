'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  TrendingUp,
  MapPin,
  Target,
  Percent,
  Bell,
  Settings,
  BarChart3,
  ChevronLeft,
  ChevronRight,
  Building2,
  Database
} from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Sales', href: '/sales', icon: TrendingUp },
  { name: 'Zones', href: '/zones', icon: MapPin },
  { name: 'Radar', href: '/radar', icon: Target },
  { name: 'Yield', href: '/yield', icon: Percent },
  { name: 'Floorplans', href: '/floorplans', icon: Building2 },
  { name: 'Data Loader', href: '/data-loader', icon: Database },
  { name: 'Alerts', href: '/alerts', icon: Bell },
  { name: 'Insights', href: '/insights', icon: BarChart3 },
  { name: 'Admin', href: '/admin', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside 
      className={cn(
        "flex flex-col bg-background-secondary border-r border-border transition-all duration-300",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Logo */}
      <div className="h-16 flex items-center justify-center border-b border-border px-4">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-accent/20 flex items-center justify-center">
            <svg width="24" height="24" viewBox="0 0 48 48" fill="none">
              <circle cx="24" cy="24" r="22" stroke="#00D9A3" strokeWidth="2" fill="none"/>
              <path d="M14 32 L24 16 L34 32" stroke="#00D9A3" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
              <path d="M18 26 L24 20 L30 26" stroke="#00D9A3" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
              <circle cx="24" cy="32" r="2" fill="#00D9A3"/>
            </svg>
          </div>
          {!collapsed && (
            <div>
              <div className="text-lg font-bold text-text-primary">Robin</div>
              <div className="text-[10px] text-text-muted tracking-wider">REAL ESTATE INTEL</div>
            </div>
          )}
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200",
                isActive 
                  ? "bg-accent/15 text-accent border border-accent/30" 
                  : "text-text-secondary hover:text-text-primary hover:bg-background-hover",
                collapsed && "justify-center px-2"
              )}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span className="font-medium text-sm">{item.name}</span>}
            </Link>
          )
        })}
      </nav>

      {/* Collapse button */}
      <div className="p-4 border-t border-border">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-full flex items-center justify-center gap-2 py-2 text-text-muted hover:text-text-primary transition-colors"
        >
          {collapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <>
              <ChevronLeft className="w-5 h-5" />
              <span className="text-sm">Collapse</span>
            </>
          )}
        </button>
      </div>
    </aside>
  )
}
