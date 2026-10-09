import { useGraphStore } from '../store/graphStore'
import type { NodeType } from '../types/nodes'

const PALETTE: { type: NodeType; label: string; cls: string }[] = [
  { type: 'scraper', label: 'Scraper', cls: 'bg-blue-50 border-blue-300 text-blue-800 hover:bg-blue-100' },
  { type: 'orchestrator', label: 'Orchestrator', cls: 'bg-purple-50 border-purple-300 text-purple-800 hover:bg-purple-100' },
  { type: 'renderer', label: 'Renderer', cls: 'bg-green-50 border-green-300 text-green-800 hover:bg-green-100' },
]

export function NodePalette() {
  const addNode = useGraphStore((s) => s.addNode)

  return (
    <div className="w-44 shrink-0 border-r border-gray-200 bg-white p-3 flex flex-col gap-2">
      <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-1">
        Add node
      </p>
      {PALETTE.map(({ type, label, cls }) => (
        <button
          key={type}
          onClick={() => addNode(type)}
          className={`px-3 py-2 rounded border text-sm font-medium text-left transition-colors cursor-pointer ${cls}`}
        >
          + {label}
        </button>
      ))}
    </div>
  )
}
