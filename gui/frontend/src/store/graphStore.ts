import { create } from 'zustand'
import {
  type Node,
  type Edge,
  type NodeChange,
  type EdgeChange,
  type Connection,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
} from '@xyflow/react'
import {
  type Registry,
  type NodeType,
  type AnyNodeData,
  type ScraperData,
  type OrchestratorData,
  type RendererData,
} from '../types/nodes'

interface GraphStore {
  nodes: Node[]
  edges: Edge[]
  selectedNodeId: string | null
  registry: Registry | null
  runOutput: string
  isRunning: boolean
  onNodesChange: (changes: NodeChange[]) => void
  onEdgesChange: (changes: EdgeChange[]) => void
  onConnect: (connection: Connection) => void
  addNode: (type: NodeType) => void
  updateNodeData: (id: string, patch: Partial<AnyNodeData>) => void
  setSelectedNode: (id: string | null) => void
  setRegistry: (registry: Registry) => void
  setRunOutput: (output: string) => void
  setIsRunning: (v: boolean) => void
}

let _counter = 0

const defaultOrchestratorData = (): OrchestratorData => ({
  llm: { provider: 'openai', config: {} },
  inference: {
    search: {
      system_prompt: 'You are a helpful research analyst.',
      task_prompt: 'Given the information, summarize the key findings relevant to the query.',
    },
    summary: {
      system_prompt: 'You are a helpful research analyst.',
      task_prompt: 'Based on all sources, provide a concise final summary. Cite your sources.',
    },
  },
})

export const useGraphStore = create<GraphStore>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  registry: null,
  runOutput: '',
  isRunning: false,

  onNodesChange: (changes) =>
    set({ nodes: applyNodeChanges(changes, get().nodes) }),

  onEdgesChange: (changes) =>
    set({ edges: applyEdgeChanges(changes, get().edges) }),

  onConnect: (connection) =>
    set({ edges: addEdge(connection, get().edges) }),

  addNode: (type) => {
    _counter += 1
    const id = `${type}-${_counter}`
    const position = { x: 80 + _counter * 40, y: 80 + _counter * 30 }

    let data: ScraperData | OrchestratorData | RendererData
    if (type === 'scraper') {
      data = { provider: get().registry?.scrapers[0] ?? 'dummy', fetch: {}, config: {} }
    } else if (type === 'orchestrator') {
      data = defaultOrchestratorData()
    } else {
      data = { provider: get().registry?.renderers[0] ?? 'markdown', output_path: '' }
    }

    set({ nodes: [...get().nodes, { id, type, position, data }] })
  },

  updateNodeData: (id, patch) =>
    set({
      nodes: get().nodes.map((n) =>
        n.id === id ? { ...n, data: { ...(n.data as Record<string, unknown>), ...patch } } : n
      ),
    }),

  setSelectedNode: (id) => set({ selectedNodeId: id }),
  setRegistry: (registry) => set({ registry }),
  setRunOutput: (output) => set({ runOutput: output }),
  setIsRunning: (v) => set({ isRunning: v }),
}))
