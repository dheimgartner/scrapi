import { useRegistry } from './hooks/useRegistry'
import { Canvas } from './components/Canvas'
import { NodePalette } from './components/NodePalette'
import { ConfigPanel } from './components/ConfigPanel'
import { Toolbar } from './components/Toolbar'
import { RunPanel } from './components/RunPanel'

export default function App() {
  useRegistry()

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <Toolbar />
      <div className="flex flex-1 overflow-hidden">
        <NodePalette />
        <Canvas />
        <ConfigPanel />
      </div>
      <RunPanel />
    </div>
  )
}
