import { useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'
import { Skeleton } from '@/components/ui/skeleton'

let mermaidInitialized = false

function initMermaid() {
  if (mermaidInitialized) return
  const isDark = document.documentElement.classList.contains('dark')
  mermaid.initialize({
    startOnLoad: false,
    theme: isDark ? 'dark' : 'default',
    securityLevel: 'loose',
  })
  mermaidInitialized = true
}

export function MermaidDiagram({ chart }: { chart: string }) {
  const [svg, setSvg] = useState<string | null>(null)
  const [error, setError] = useState(false)
  const idRef = useRef(`mermaid-${Math.random().toString(36).slice(2)}`)

  useEffect(() => {
    initMermaid()
    mermaid.render(idRef.current, chart)
      .then(({ svg }) => setSvg(svg))
      .catch(() => setError(true))
  }, [chart])

  if (error) {
    return (
      <pre className="bg-muted rounded p-4 overflow-x-auto">
        <code className="text-sm">{chart}</code>
      </pre>
    )
  }
  if (!svg) return <Skeleton className="h-48 w-full" />
  return <div className="my-4" dangerouslySetInnerHTML={{ __html: svg }} />
}
