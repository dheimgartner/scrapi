import { useGraphStore } from '../store/graphStore'
import type { ScraperData, OrchestratorData, RendererData } from '../types/nodes'

function Label({ children }: { children: React.ReactNode }) {
  return <label className="text-xs font-medium text-gray-500">{children}</label>
}

function Field({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <div className="flex flex-col gap-1">
      <Label>{label}</Label>
      <input
        className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-400"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  )
}

function TextArea({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <div className="flex flex-col gap-1">
      <Label>{label}</Label>
      <textarea
        className="border border-gray-300 rounded px-2 py-1 text-sm resize-none focus:outline-none focus:ring-1 focus:ring-indigo-400"
        rows={3}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  )
}

function Select({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (v: string) => void }) {
  return (
    <div className="flex flex-col gap-1">
      <Label>{label}</Label>
      <select
        className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-400"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {options.map((o) => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>
    </div>
  )
}

function SectionHeader({ children }: { children: React.ReactNode }) {
  return (
    <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mt-3 mb-1">
      {children}
    </div>
  )
}

function ScraperForm({ id, data }: { id: string; data: ScraperData }) {
  const { updateNodeData, registry } = useGraphStore()
  return (
    <div className="flex flex-col gap-3">
      <Select
        label="Provider"
        value={data.provider}
        options={registry?.scrapers ?? [data.provider]}
        onChange={(v) => updateNodeData(id, { provider: v })}
      />
      <div className="flex flex-col gap-1">
        <Label>Fetch config (JSON)</Label>
        <textarea
          className="border border-gray-300 rounded px-2 py-1 text-xs font-mono resize-none focus:outline-none focus:ring-1 focus:ring-indigo-400"
          rows={5}
          defaultValue={JSON.stringify(data.fetch, null, 2)}
          onBlur={(e) => {
            try {
              updateNodeData(id, { fetch: JSON.parse(e.target.value) })
            } catch {
              // leave as-is on parse error
            }
          }}
        />
        <span className="text-[10px] text-gray-400">
          e.g. {'{"query": "AI news", "n": 5}'}
        </span>
      </div>
    </div>
  )
}

function OrchestratorForm({ id, data }: { id: string; data: OrchestratorData }) {
  const { updateNodeData, registry } = useGraphStore()

  const patchLlm = (patch: Partial<OrchestratorData['llm']>) =>
    updateNodeData(id, { llm: { ...data.llm, ...patch } } as Partial<OrchestratorData>)

  const patchSearch = (patch: Partial<OrchestratorData['inference']['search']>) =>
    updateNodeData(id, {
      inference: { ...data.inference, search: { ...data.inference.search, ...patch } },
    } as Partial<OrchestratorData>)

  const patchSummary = (patch: Partial<OrchestratorData['inference']['summary']>) =>
    updateNodeData(id, {
      inference: { ...data.inference, summary: { ...data.inference.summary, ...patch } },
    } as Partial<OrchestratorData>)

  return (
    <div className="flex flex-col gap-2">
      <SectionHeader>LLM</SectionHeader>
      <Select
        label="Provider"
        value={data.llm.provider}
        options={registry?.llms ?? [data.llm.provider]}
        onChange={(v) => patchLlm({ provider: v })}
      />
      <SectionHeader>Search inference</SectionHeader>
      <TextArea
        label="System prompt"
        value={data.inference.search.system_prompt}
        onChange={(v) => patchSearch({ system_prompt: v })}
      />
      <TextArea
        label="Task prompt"
        value={data.inference.search.task_prompt}
        onChange={(v) => patchSearch({ task_prompt: v })}
      />
      <SectionHeader>Summary inference</SectionHeader>
      <TextArea
        label="System prompt"
        value={data.inference.summary.system_prompt}
        onChange={(v) => patchSummary({ system_prompt: v })}
      />
      <TextArea
        label="Task prompt"
        value={data.inference.summary.task_prompt}
        onChange={(v) => patchSummary({ task_prompt: v })}
      />
    </div>
  )
}

function RendererForm({ id, data }: { id: string; data: RendererData }) {
  const { updateNodeData, registry } = useGraphStore()
  return (
    <div className="flex flex-col gap-3">
      <Select
        label="Provider"
        value={data.provider}
        options={registry?.renderers ?? [data.provider]}
        onChange={(v) => updateNodeData(id, { provider: v })}
      />
      <Field
        label="Output path"
        value={data.output_path}
        onChange={(v) => updateNodeData(id, { output_path: v })}
      />
    </div>
  )
}

export function ConfigPanel() {
  const { nodes, selectedNodeId } = useGraphStore()
  const node = nodes.find((n) => n.id === selectedNodeId)

  if (!node) {
    return (
      <div className="w-72 shrink-0 border-l border-gray-200 bg-white flex items-center justify-center">
        <p className="text-sm text-gray-400 px-4 text-center">
          Select a node to configure it.
        </p>
      </div>
    )
  }

  return (
    <div className="w-72 shrink-0 border-l border-gray-200 bg-white overflow-y-auto p-4">
      <p className="text-xs font-mono text-gray-400 mb-3">{node.id}</p>
      {node.type === 'scraper' && (
        <ScraperForm id={node.id} data={node.data as ScraperData} />
      )}
      {node.type === 'orchestrator' && (
        <OrchestratorForm id={node.id} data={node.data as OrchestratorData} />
      )}
      {node.type === 'renderer' && (
        <RendererForm id={node.id} data={node.data as RendererData} />
      )}
    </div>
  )
}
