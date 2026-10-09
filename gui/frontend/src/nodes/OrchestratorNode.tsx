import { Handle, Position, type NodeProps } from '@xyflow/react'
import type { OrchestratorData } from '../types/nodes'

export function OrchestratorNode({ data, selected }: NodeProps) {
  const d = data as OrchestratorData
  return (
    <div
      className={`px-3 py-2 rounded-md border-2 bg-purple-50 min-w-[160px] ${
        selected ? 'border-purple-500 shadow-md' : 'border-purple-300'
      }`}
    >
      <Handle type="target" position={Position.Left} />
      <div className="text-[10px] font-bold text-purple-600 uppercase tracking-wider mb-1">
        Orchestrator
      </div>
      <div className="text-sm font-semibold text-gray-800">{d.llm?.provider || '—'}</div>
      <Handle type="source" position={Position.Right} />
    </div>
  )
}
