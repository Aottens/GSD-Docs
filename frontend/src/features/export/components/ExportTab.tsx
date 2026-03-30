import { useState } from 'react'
import { Separator } from '@/components/ui/separator'
import { ExportOptions } from './ExportOptions'
import { AssemblyPipeline } from './AssemblyPipeline'
import { VersionHistory } from './VersionHistory'

interface ExportTabProps {
  projectId: number
  language: string
  onNavigateToDocs?: () => void
}

export function ExportTab({ projectId, language, onNavigateToDocs }: ExportTabProps) {
  const [mode, setMode] = useState('draft')
  const [exportLanguage, setExportLanguage] = useState(language)

  return (
    <div className="space-y-8 p-6">
      <h1 className="text-2xl font-semibold">Exporteren</h1>

      <ExportOptions
        mode={mode}
        language={exportLanguage}
        onModeChange={setMode}
        onLanguageChange={setExportLanguage}
        disabled={false}
      />

      <AssemblyPipeline projectId={projectId} mode={mode} language={exportLanguage} onNavigateToDocs={onNavigateToDocs} />

      <Separator />

      <VersionHistory projectId={projectId} />
    </div>
  )
}
