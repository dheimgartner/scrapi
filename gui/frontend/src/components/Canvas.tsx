import { useCallback } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  type NodeMouseHandler,
} from '@xyflow/react'
import { useGraphStore } from '../store/graphStore'
import { ScraperNode } from '../nodes/ScraperNode'
import { OrchestratorNode } from '../nodes/OrchestratorNode'
import { RendererNode } from '../nodes/RendererNode'

const nodeTypes = {
  scraper: ScraperNode,
  orchestrator: OrchestratorNode,
  renderer: RendererNode,
}

export function Canvas() {
  const { nodes, edges, onNodesChange, onEdgesChange, onConnect, setSelectedNode } =
    useGraphStore()

  const handleNodeClick: NodeMouseHandler = useCallback(
    (_e, node) => setSelectedNode(node.id),
    [setSelectedNode],
  )

  const handlePaneClick = useCallback(() => setSelectedNode(null), [setSelectedNode])

  return (
    <div className="flex-1 h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={handleNodeClick}
        onPaneClick={handlePaneClick}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  )
}
