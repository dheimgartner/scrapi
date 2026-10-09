import { Handle, Position, type NodeProps } from '@xyflow/react'
import type { ScraperData } from '../types/nodes'

export function ScraperNode({ data, selected }: NodeProps) {
  const d = data as ScraperData
  return (
    <div
      className={`px-3 py-2 rounded-md border-2 bg-blue-50 min-w-[144px] ${
        selected ? 'border-blue-500 shadow-md' : 'border-blue-300'
      }`}
    >
      <div className="text-[10px] font-bold text-blue-600 uppercase tracking-wider mb-1">
        Scraper
      </div>
      <div className="text-sm font-semibold text-gray-800">{d.provider || '—'}</div>
      <Handle type="source" position={Position.Right} />
    </div>
  )
}
