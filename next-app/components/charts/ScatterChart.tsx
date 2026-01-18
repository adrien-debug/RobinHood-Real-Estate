'use client'

import {
  ScatterChart as RechartsScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ZAxis,
} from 'recharts'
import { cn } from '@/lib/utils'

interface ScatterChartProps {
  data: Array<Record<string, unknown>>
  xKey: string
  yKey: string
  zKey?: string
  color?: string
  height?: number
  className?: string
  showGrid?: boolean
  xLabel?: string
  yLabel?: string
}

export function ScatterChart({
  data,
  xKey,
  yKey,
  zKey,
  color = '#10B981',
  height = 300,
  className,
  showGrid = true,
  xLabel,
  yLabel,
}: ScatterChartProps) {
  return (
    <div className={cn("w-full", className)} style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsScatterChart margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          {showGrid && (
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="rgba(255,255,255,0.05)"
            />
          )}
          <XAxis 
            dataKey={xKey}
            name={xLabel || xKey}
            stroke="rgba(255,255,255,0.3)"
            fontSize={11}
            tickLine={false}
            axisLine={false}
          />
          <YAxis 
            dataKey={yKey}
            name={yLabel || yKey}
            stroke="rgba(255,255,255,0.3)"
            fontSize={11}
            tickLine={false}
            axisLine={false}
          />
          {zKey && (
            <ZAxis dataKey={zKey} range={[50, 400]} />
          )}
          <Tooltip
            contentStyle={{
              backgroundColor: '#131D32',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '8px',
              color: '#fff',
            }}
          />
          <Scatter
            data={data}
            fill={color}
            fillOpacity={0.7}
          />
        </RechartsScatterChart>
      </ResponsiveContainer>
    </div>
  )
}
