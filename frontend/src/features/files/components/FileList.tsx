import { Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { FileTypeIcon } from './FileTypeIcon'
import { formatBytes, formatDate } from '@/lib/utils'
import type { FileMetadata } from '../types/file'

interface FileListProps {
  files: FileMetadata[]
  onFileClick: (file: FileMetadata) => void
  showOverrideAction?: boolean
  onOverride?: (file: FileMetadata) => void
}

function getMimeTypeLabel(mimeType: string): string {
  if (mimeType === 'application/pdf') return 'PDF'
  if (mimeType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    return 'DOCX'
  if (mimeType === 'application/msword') return 'DOC'
  if (mimeType.startsWith('image/png')) return 'PNG'
  if (mimeType.startsWith('image/jpeg')) return 'JPG'
  if (mimeType.startsWith('image/')) return 'Afbeelding'
  return 'Bestand'
}

export function FileList({
  files,
  onFileClick,
  showOverrideAction = false,
  onOverride,
}: FileListProps) {
  if (files.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <Upload className="h-12 w-12 text-muted-foreground/50 mb-4" />
        <p className="text-muted-foreground">Geen bestanden gevonden</p>
      </div>
    )
  }

  return (
    <div className="border rounded-lg overflow-hidden">
      <table className="w-full">
        <thead className="bg-muted/50 border-b">
          <tr>
            <th className="text-left px-4 py-3 text-sm font-medium">Bestandsnaam</th>
            <th className="text-left px-4 py-3 text-sm font-medium w-24">Type</th>
            <th className="text-left px-4 py-3 text-sm font-medium w-32">Grootte</th>
            <th className="text-left px-4 py-3 text-sm font-medium w-40">Geüpload</th>
            {showOverrideAction && (
              <th className="text-left px-4 py-3 text-sm font-medium w-32">Actie</th>
            )}
          </tr>
        </thead>
        <tbody>
          {files.map((file) => (
            <tr
              key={file.id}
              className="border-b last:border-b-0 hover:bg-muted/30 cursor-pointer transition-colors"
              onClick={() => onFileClick(file)}
            >
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <FileTypeIcon mimeType={file.mime_type} />
                  <span className="text-sm truncate">{file.original_filename}</span>
                </div>
              </td>
              <td className="px-4 py-3 text-sm text-muted-foreground">
                {getMimeTypeLabel(file.mime_type)}
              </td>
              <td className="px-4 py-3 text-sm text-muted-foreground">
                {formatBytes(file.size_bytes)}
              </td>
              <td className="px-4 py-3 text-sm text-muted-foreground">
                {formatDate(file.uploaded_at)}
              </td>
              {showOverrideAction && (
                <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onOverride?.(file)}
                  >
                    Overschrijven
                  </Button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
