import { Handle, Position, type NodeProps } from '@xyflow/react'
import type { RendererData } from '../types/nodes'

export function RendererNode({ data, selected }: NodeProps) {
  const d = data as RendererData
  return (
    <div
      className={`px-3 py-2 rounded-md border-2 bg-green-50 min-w-[144px] ${
        selected ? 'border-green-500 shadow-md' : 'border-green-300'
      }`}
    >
      <Handle type="target" position={Position.Left} />
      <div className="text-[10px] font-bold text-green-600 uppercase tracking-wider mb-1">
        Renderer
      </div>
      <div className="text-sm font-semibold text-gray-800">{d.provider || '—'}</div>
    </div>
  )
}
