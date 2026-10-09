export interface Registry {
  scrapers: string[]
  llms: string[]
  renderers: string[]
}

export interface ScraperData {
  provider: string
  fetch: Record<string, unknown>
  config: Record<string, unknown>
}

export interface OrchestratorData {
  llm: {
    provider: string
    config: Record<string, unknown>
  }
  inference: {
    search: { system_prompt: string; task_prompt: string }
    summary: { system_prompt: string; task_prompt: string }
  }
}

export interface RendererData {
  provider: string
  output_path: string
}

export type NodeType = 'scraper' | 'orchestrator' | 'renderer'
export type AnyNodeData = ScraperData | OrchestratorData | RendererData
