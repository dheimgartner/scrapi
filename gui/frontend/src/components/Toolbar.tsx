import { useGraphStore } from '../store/graphStore'

export function Toolbar() {
  const { nodes, edges, isRunning, setRunOutput, setIsRunning } = useGraphStore()

  const payload = () => ({
    nodes: nodes.map((n) => ({ id: n.id, type: n.type, data: n.data })),
    edges: edges.map((e) => ({ id: e.id, source: e.source, target: e.target })),
  })

  const handleExport = async () => {
    const res = await fetch('/api/graph/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload()),
    })
    if (!res.ok) {
      const err = await res.json()
      alert(`Export failed: ${err.detail}`)
      return
    }
    const text = await res.text()
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'scrapi_config.toml'
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleRun = async () => {
    setIsRunning(true)
    setRunOutput('')

    const res = await fetch('/api/graph/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload()),
    })

    const reader = res.body?.getReader()
    const decoder = new TextDecoder()
    let accumulated = ''

    while (reader) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value, { stream: true })
      for (const line of chunk.split('\n')) {
        if (!line.startsWith('data: ')) continue
        try {
          const msg = JSON.parse(line.slice(6)) as { status: string; message: string }
          accumulated += (accumulated ? '\n' : '') + `[${msg.status}] ${msg.message}`
          setRunOutput(accumulated)
        } catch {
          // skip malformed lines
        }
      }
    }

    setIsRunning(false)
  }

  return (
    <div className="h-12 shrink-0 border-b border-gray-200 bg-white flex items-center px-4 gap-3">
      <span className="text-base font-bold text-gray-800 mr-3">Scrapi</span>
      <button
        onClick={handleExport}
        className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-50 transition-colors"
      >
        Export TOML
      </button>
      <button
        onClick={handleRun}
        disabled={isRunning}
        className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 transition-colors"
      >
        {isRunning ? 'Running…' : '▶ Run'}
      </button>
    </div>
  )
}
