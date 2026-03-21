import { useRef, useState, useCallback } from 'react'
import type { PipelineStage, ExportProgressEvent } from '@/types/export'

const INITIAL_STAGES: PipelineStage[] = [
  { step: 0, name: 'Cross-referenties oplossen', status: 'idle' },
  { step: 1, name: 'Secties samenvoegen', status: 'idle' },
  { step: 2, name: 'DOCX genereren', status: 'idle' },
  { step: 3, name: 'Diagrammen renderen', status: 'idle' },
]

export function useAssemblyStream(projectId: number) {
  const [stages, setStages] = useState<PipelineStage[]>(INITIAL_STAGES)
  const [isRunning, setIsRunning] = useState(false)
  const [completedFilename, setCompletedFilename] = useState<string | null>(null)
  const eventSourceRef = useRef<EventSource | null>(null)

  const start = useCallback(
    (options: { mode: string; language: string }) => {
      // Clean up any existing connection
      eventSourceRef.current?.close()

      // Reset state
      setStages(INITIAL_STAGES.map(s => ({ ...s, status: 'idle' as const })))
      setIsRunning(true)
      setCompletedFilename(null)

      const url = `/api/projects/${projectId}/export/stream?mode=${options.mode}&language=${options.language}`
      const eventSource = new EventSource(url)
      eventSourceRef.current = eventSource

      // Track whether we finished cleanly to ignore post-close error events
      let finished = false

      // SSE backend sends named events: step_start, step_done, complete, error, cancelled
      eventSource.addEventListener('step_start', (event: MessageEvent) => {
        try {
          const data: ExportProgressEvent = JSON.parse(event.data)
          setStages(prev =>
            prev.map(s =>
              s.step === data.step ? { ...s, status: 'running' } : s
            )
          )
        } catch { /* ignore */ }
      })

      eventSource.addEventListener('step_done', (event: MessageEvent) => {
        try {
          const data: ExportProgressEvent = JSON.parse(event.data)
          setStages(prev =>
            prev.map(s =>
              s.step === data.step ? { ...s, status: 'done' } : s
            )
          )
        } catch { /* ignore */ }
      })

      eventSource.addEventListener('complete', (event: MessageEvent) => {
        finished = true
        try {
          const data: ExportProgressEvent = JSON.parse(event.data)
          if (data.artifact_filename) {
            setCompletedFilename(data.artifact_filename)
          }
        } catch { /* ignore */ }
        setIsRunning(false)
        eventSource.close()
        eventSourceRef.current = null
      })

      // Named "error" event from server (pipeline failure)
      eventSource.addEventListener('error', (event) => {
        if (finished) return
        // Server-sent error events are MessageEvents with data
        if (event instanceof MessageEvent && event.data) {
          finished = true
          try {
            const data: ExportProgressEvent = JSON.parse(event.data)
            setStages(prev =>
              prev.map(s =>
                s.step === data.step
                  ? { ...s, status: 'error', errorMessage: data.message }
                  : s
              )
            )
          } catch { /* ignore */ }
          setIsRunning(false)
          eventSource.close()
          eventSourceRef.current = null
        }
        // Native connection errors (Event, not MessageEvent) are handled by onerror below
      })

      eventSource.addEventListener('cancelled', () => {
        finished = true
        setStages(INITIAL_STAGES.map(s => ({ ...s, status: 'idle' as const })))
        setIsRunning(false)
        eventSource.close()
        eventSourceRef.current = null
      })

      // Native connection error — fires when SSE connection drops
      eventSource.onerror = () => {
        if (finished) return // Expected after complete/error/cancelled close
        // Unexpected connection loss
        setIsRunning(false)
        eventSource.close()
        eventSourceRef.current = null
      }
    },
    [projectId]
  )

  const cancel = useCallback(() => {
    eventSourceRef.current?.close()
    eventSourceRef.current = null
    setIsRunning(false)
    setStages(INITIAL_STAGES.map(s => ({ ...s, status: 'idle' as const })))
  }, [])

  return { stages, isRunning, start, cancel, completedFilename }
}
