'use client'

import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { cn } from '@/lib/utils'

interface BarChartProps {
  data: Array<Record<string, unknown>>
  dataKey: string
  xAxisKey?: string
  color?: string
  colors?: string[]
  height?: number
  className?: string
  horizontal?: boolean
  showGrid?: boolean
  showXAxis?: boolean
  showYAxis?: boolean
  showLabels?: boolean
}

export function BarChart({
  data,
  dataKey,
  xAxisKey = 'name',
  color = '#10B981',
  colors,
  height = 300,
  className,
  horizontal = false,
  showGrid = true,
  showXAxis = true,
  showYAxis = true,
  showLabels = false,
}: BarChartProps) {
  const defaultColors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6']

  return (
    <div className={cn("w-full", className)} style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsBarChart 
          data={data} 
          layout={horizontal ? 'vertical' : 'horizontal'}
          margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
        >
          {showGrid && (
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="rgba(255,255,255,0.05)" 
              horizontal={!horizontal}
              vertical={horizontal}
            />
          )}
          {horizontal ? (
            <>
              {showYAxis && (
                <YAxis 
                  dataKey={xAxisKey}
                  type="category"
                  stroke="rgba(255,255,255,0.3)"
                  fontSize={10}
                  tickLine={false}
                  axisLine={false}
                  width={80}
                />
              )}
              {showXAxis && (
                <XAxis 
                  type="number"
                  stroke="rgba(255,255,255,0.3)"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                />
              )}
            </>
          ) : (
            <>
              {showXAxis && (
                <XAxis 
                  dataKey={xAxisKey}
                  stroke="rgba(255,255,255,0.3)"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                />
              )}
              {showYAxis && (
                <YAxis 
                  stroke="rgba(255,255,255,0.3)"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                />
              )}
            </>
          )}
          <Tooltip
            contentStyle={{
              backgroundColor: '#131D32',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '8px',
              color: '#fff',
            }}
          />
          <Bar 
            dataKey={dataKey} 
            radius={[4, 4, 0, 0]}
            label={showLabels ? { 
              position: horizontal ? 'right' : 'top', 
              fill: '#fff', 
              fontSize: 11 
            } : false}
          >
            {data.map((_, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={colors ? colors[index % colors.length] : (color || defaultColors[index % defaultColors.length])}
              />
            ))}
          </Bar>
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  )
}
