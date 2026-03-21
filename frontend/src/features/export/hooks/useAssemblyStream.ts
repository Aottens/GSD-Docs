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

      eventSource.onmessage = (event) => {
        try {
          const data: ExportProgressEvent = JSON.parse(event.data)

          if (data.event === 'step_start') {
            setStages(prev =>
              prev.map(s =>
                s.step === data.step ? { ...s, status: 'running' } : s
              )
            )
          } else if (data.event === 'step_done') {
            setStages(prev =>
              prev.map(s =>
                s.step === data.step ? { ...s, status: 'done' } : s
              )
            )
          } else if (data.event === 'complete') {
            if (data.artifact_filename) {
              setCompletedFilename(data.artifact_filename)
            }
            setIsRunning(false)
            eventSource.close()
            eventSourceRef.current = null
          } else if (data.event === 'error') {
            setStages(prev =>
              prev.map(s =>
                s.step === data.step
                  ? { ...s, status: 'error', errorMessage: data.message }
                  : s
              )
            )
            setIsRunning(false)
            eventSource.close()
            eventSourceRef.current = null
          } else if (data.event === 'cancelled') {
            setStages(INITIAL_STAGES.map(s => ({ ...s, status: 'idle' as const })))
            setIsRunning(false)
            eventSource.close()
            eventSourceRef.current = null
          }
        } catch {
          // Ignore parse errors
        }
      }

      eventSource.onerror = () => {
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
