import { FileUploadZone } from '@/features/files/components/FileUploadZone'
import type { UploadProgress } from '@/features/files/types/file'

interface Step4ReferenceUploadProps {
  onFilesSelected: (files: File[]) => void
  progressMap: Map<string, UploadProgress>
}

export function Step4ReferenceUpload({
  onFilesSelected,
  progressMap,
}: Step4ReferenceUploadProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold mb-2">Referentiebestanden uploaden</h2>
        <p className="text-muted-foreground">
          Upload P&IDs, specificaties en andere referentiedocumenten voor dit project. U kunt dit
          ook later doen.
        </p>
      </div>

      <FileUploadZone onFilesSelected={onFilesSelected} progressMap={progressMap} />

      <div className="bg-muted/30 border border-muted rounded-lg p-4">
        <p className="text-sm text-muted-foreground">
          <strong>Tip:</strong> Bestanden worden na het aanmaken van het project geüpload. U kunt
          deze stap overslaan en later bestanden toevoegen via de Referenties sectie in het
          project.
        </p>
      </div>
    </div>
  )
}
