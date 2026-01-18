'use client'

import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts'
import { cn } from '@/lib/utils'

interface PieChartProps {
  data: Array<{ name: string; value: number }>
  colors?: string[]
  height?: number
  className?: string
  innerRadius?: number
  outerRadius?: number
  showLegend?: boolean
  showLabels?: boolean
  centerLabel?: string | number
}

const DEFAULT_COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#6B7280']

export function PieChart({
  data,
  colors = DEFAULT_COLORS,
  height = 250,
  className,
  innerRadius = 60,
  outerRadius = 80,
  showLegend = false,
  showLabels = true,
  centerLabel,
}: PieChartProps) {
  return (
    <div className={cn("w-full relative", className)} style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsPieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={innerRadius}
            outerRadius={outerRadius}
            paddingAngle={2}
            dataKey="value"
            label={showLabels ? ({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%` : false}
            labelLine={showLabels}
          >
            {data.map((_, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={colors[index % colors.length]}
                stroke="transparent"
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#131D32',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '8px',
              color: '#fff',
            }}
          />
          {showLegend && (
            <Legend 
              verticalAlign="bottom"
              height={36}
              wrapperStyle={{ color: 'rgba(255,255,255,0.7)', fontSize: '12px' }}
            />
          )}
        </RechartsPieChart>
      </ResponsiveContainer>
      
      {/* Center label for donut charts */}
      {centerLabel !== undefined && innerRadius > 0 && (
        <div 
          className="absolute inset-0 flex items-center justify-center pointer-events-none"
          style={{ marginTop: showLegend ? -18 : 0 }}
        >
          <div className="text-center">
            <div className="text-2xl font-bold text-text-primary">{centerLabel}</div>
          </div>
        </div>
      )}
    </div>
  )
}
