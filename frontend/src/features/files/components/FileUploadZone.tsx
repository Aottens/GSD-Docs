import { useCallback } from 'react'
import { useDropzone, type FileRejection } from 'react-dropzone'
import { Upload, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'
import type { UploadProgress } from '../types/file'

interface FileUploadZoneProps {
  onFilesSelected: (files: File[]) => void
  acceptedTypes?: Record<string, string[]>
  maxSizeMB?: number
  disabled?: boolean
  progressMap?: Map<string, UploadProgress>
}

const DEFAULT_ACCEPTED_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'application/msword': ['.doc'],
  'image/png': ['.png'],
  'image/jpeg': ['.jpg', '.jpeg'],
}

export function FileUploadZone({
  onFilesSelected,
  acceptedTypes = DEFAULT_ACCEPTED_TYPES,
  maxSizeMB = 50,
  disabled = false,
  progressMap = new Map(),
}: FileUploadZoneProps) {
  const maxSizeBytes = maxSizeMB * 1024 * 1024

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      onFilesSelected(acceptedFiles)
    },
    [onFilesSelected]
  )

  const onDropRejected = useCallback(
    (fileRejections: FileRejection[]) => {
      fileRejections.forEach((rejection) => {
        rejection.errors.forEach((error) => {
          if (error.code === 'file-too-large') {
            toast.error(`${rejection.file.name} is te groot (max ${maxSizeMB}MB)`)
          } else if (error.code === 'file-invalid-type') {
            toast.error(`${rejection.file.name}: bestandstype niet toegestaan`)
          } else {
            toast.error(`${rejection.file.name}: ${error.message}`)
          }
        })
      })
    },
    [maxSizeMB]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDropRejected,
    accept: acceptedTypes,
    maxSize: maxSizeBytes,
    disabled,
  })

  const acceptedExtensions = Object.values(acceptedTypes)
    .flat()
    .join(', ')
    .toUpperCase()

  return (
    <div className="space-y-4">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed rounded-lg p-8 transition-colors cursor-pointer',
          isDragActive
            ? 'border-primary bg-primary/5'
            : 'border-muted-foreground/25 hover:border-muted-foreground/50',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center gap-4 text-center">
          <Upload className="h-10 w-10 text-muted-foreground" />
          <div>
            <p className="text-sm font-medium">
              {isDragActive ? 'Drop bestanden hier' : 'Sleep bestanden hierheen'}
            </p>
            <Button variant="outline" className="mt-2" type="button">
              Of kies bestanden
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">
            Toegestaan: {acceptedExtensions} (max {maxSizeMB}MB)
          </p>
        </div>
      </div>

      {/* Progress Bars */}
      {progressMap.size > 0 && (
        <div className="space-y-2">
          {Array.from(progressMap.entries()).map(([filename, progress]) => (
            <div key={filename} className="flex items-center gap-3 p-3 bg-muted/50 rounded-md">
              {/* Status Icon */}
              {progress.status === 'done' && (
                <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
              )}
              {progress.status === 'error' && (
                <AlertCircle className="h-4 w-4 text-destructive shrink-0" />
              )}
              {(progress.status === 'uploading' || progress.status === 'validating') && (
                <Loader2 className="h-4 w-4 text-primary animate-spin shrink-0" />
              )}
              {progress.status === 'pending' && (
                <div className="h-4 w-4 rounded-full border-2 border-muted-foreground/25 shrink-0" />
              )}

              {/* Filename and Progress */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{filename}</p>
                {progress.status === 'uploading' && (
                  <Progress value={progress.progress} className="h-1 mt-1" />
                )}
              </div>

              {/* Status Text */}
              <div className="text-xs text-muted-foreground shrink-0">
                {progress.status === 'pending' && 'Wachten...'}
                {progress.status === 'uploading' && `${progress.progress}%`}
                {progress.status === 'validating' && 'Valideren...'}
                {progress.status === 'done' && (
                  <span className="text-green-600 font-medium">Gereed</span>
                )}
                {progress.status === 'error' && (
                  <span className="text-destructive font-medium">
                    {progress.error || 'Fout'}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
