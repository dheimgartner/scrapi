import { useEffect } from 'react'
import { useGraphStore } from '../store/graphStore'

export function useRegistry() {
  const setRegistry = useGraphStore((s) => s.setRegistry)

  useEffect(() => {
    fetch('/api/registry')
      .then((r) => r.json())
      .then(setRegistry)
      .catch(console.error)
  }, [setRegistry])
}
