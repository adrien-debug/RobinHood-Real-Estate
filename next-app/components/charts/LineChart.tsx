'use client'

import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from 'recharts'
import { cn } from '@/lib/utils'

interface LineData {
  dataKey: string
  color: string
  name?: string
  strokeDasharray?: string
}

interface LineChartProps {
  data: Array<Record<string, unknown>>
  lines: LineData[]
  xAxisKey?: string
  height?: number
  className?: string
  showGrid?: boolean
  showXAxis?: boolean
  showYAxis?: boolean
  showLegend?: boolean
  referenceLines?: Array<{ y: number; color: string; label?: string }>
}

export function LineChart({
  data,
  lines,
  xAxisKey = 'name',
  height = 300,
  className,
  showGrid = true,
  showXAxis = true,
  showYAxis = true,
  showLegend = false,
  referenceLines = [],
}: LineChartProps) {
  return (
    <div className={cn("w-full", className)} style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsLineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          {showGrid && (
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="rgba(255,255,255,0.05)" 
              vertical={false}
            />
          )}
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
              tickFormatter={(value) => value.toLocaleString()}
            />
          )}
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
              wrapperStyle={{ color: 'rgba(255,255,255,0.7)', fontSize: '12px' }}
            />
          )}
          
          {referenceLines.map((refLine, index) => (
            <ReferenceLine
              key={index}
              y={refLine.y}
              stroke={refLine.color}
              strokeDasharray="3 3"
              label={refLine.label ? {
                value: refLine.label,
                fill: refLine.color,
                fontSize: 10,
              } : undefined}
            />
          ))}
          
          {lines.map((line) => (
            <Line
              key={line.dataKey}
              type="monotone"
              dataKey={line.dataKey}
              stroke={line.color}
              strokeWidth={2}
              strokeDasharray={line.strokeDasharray}
              dot={false}
              activeDot={{ r: 4, fill: line.color }}
              name={line.name || line.dataKey}
            />
          ))}
        </RechartsLineChart>
      </ResponsiveContainer>
    </div>
  )
}
