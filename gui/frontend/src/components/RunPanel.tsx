import { useGraphStore } from '../store/graphStore'

export function RunPanel() {
  const { runOutput, isRunning } = useGraphStore()

  if (!runOutput && !isRunning) return null

  return (
    <div className="h-48 shrink-0 border-t border-gray-200 bg-gray-950 text-green-400 font-mono text-xs p-3 overflow-y-auto">
      {isRunning && <span className="text-yellow-400 animate-pulse">● Running…{'\n'}</span>}
      <pre className="whitespace-pre-wrap mt-1">{runOutput}</pre>
    </div>
  )
}
