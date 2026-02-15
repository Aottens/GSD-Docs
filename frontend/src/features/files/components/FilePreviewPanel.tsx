import { useState, useEffect, useRef } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import { ChevronLeft, ChevronRight, AlertCircle } from 'lucide-react'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { FileActions } from './FileActions'
import { DeleteConfirmation } from './DeleteConfirmation'
import { useDeleteFile, useUpdateFile, useReplaceFile } from '../hooks/useFiles'
import { formatBytes, formatDate } from '@/lib/utils'
import type { FileMetadata, FolderInfo } from '../types/file'

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`

interface FilePreviewPanelProps {
  file: FileMetadata | null
  open: boolean
  onOpenChange: (open: boolean) => void
  folders: FolderInfo[]
  onFileUpdated: () => void
  readOnly?: boolean
}

export function FilePreviewPanel({
  file,
  open,
  onOpenChange,
  folders,
  onFileUpdated,
  readOnly = false,
}: FilePreviewPanelProps) {
  const [numPages, setNumPages] = useState<number>(0)
  const [pageNumber, setPageNumber] = useState(1)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [docxError, setDocxError] = useState(false)
  const docxContainerRef = useRef<HTMLDivElement>(null)

  // Mutations
  const deleteMutation = useDeleteFile()
  const updateMutation = useUpdateFile()
  const replaceMutation = useReplaceFile()

  // Reset page number when file changes
  useEffect(() => {
    setPageNumber(1)
    setDocxError(false)
  }, [file?.id])

  // Render DOCX preview
  useEffect(() => {
    if (
      file &&
      (file.mime_type.includes('word') ||
        file.mime_type.includes('openxmlformats')) &&
      docxContainerRef.current
    ) {
      const renderDocx = async () => {
        try {
          const docxPreview = await import('docx-preview')
          const response = await fetch(`/api/files/${file.id}/preview`)
          const blob = await response.blob()

          if (docxContainerRef.current) {
            docxContainerRef.current.innerHTML = '' // Clear previous content
            await docxPreview.renderAsync(blob, docxContainerRef.current)
          }
        } catch (error) {
          console.error('Failed to render DOCX:', error)
          setDocxError(true)
        }
      }
      renderDocx()
    }
  }, [file?.id])

  if (!file) return null

  const previewUrl = `/api/files/${file.id}/preview`

  const handleRename = (newName: string) => {
    updateMutation.mutate(
      { fileId: file.id, updates: { original_filename: newName } },
      { onSuccess: onFileUpdated }
    )
  }

  const handleMove = (folderId: number | null) => {
    updateMutation.mutate(
      { fileId: file.id, updates: { folder_id: folderId } },
      { onSuccess: onFileUpdated }
    )
  }

  const handleReplace = (newFile: File) => {
    replaceMutation.mutate(
      { fileId: file.id, newFile },
      { onSuccess: onFileUpdated }
    )
  }

  const handleDelete = () => {
    deleteMutation.mutate(file.id, {
      onSuccess: () => {
        onFileUpdated()
        onOpenChange(false)
      },
    })
  }

  const handleDownload = () => {
    window.open(file.download_url, '_blank')
  }

  const getMimeTypeLabel = (mimeType: string): string => {
    if (mimeType === 'application/pdf') return 'PDF'
    if (mimeType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
      return 'DOCX'
    if (mimeType === 'application/msword') return 'DOC'
    if (mimeType.startsWith('image/png')) return 'PNG'
    if (mimeType.startsWith('image/jpeg')) return 'JPG'
    if (mimeType.startsWith('image/')) return 'Afbeelding'
    return 'Bestand'
  }

  const getFolderName = () => {
    if (!file.folder_id) return 'Root'
    const folder = folders.find((f) => f.id === file.folder_id)
    return folder?.name || 'Root'
  }

  return (
    <>
      <Sheet open={open} onOpenChange={onOpenChange}>
        <SheetContent side="right" className="w-3/4 sm:max-w-2xl overflow-y-auto">
          <SheetHeader>
            <SheetTitle>{file.original_filename}</SheetTitle>
          </SheetHeader>

          <div className="mt-6 space-y-6">
            {/* Preview Area */}
            <div className="border rounded-lg p-4 bg-muted/30">
              {/* Images */}
              {file.mime_type.startsWith('image/') && (
                <img
                  src={previewUrl}
                  alt={file.original_filename}
                  className="w-full h-auto rounded"
                />
              )}

              {/* PDF */}
              {file.mime_type === 'application/pdf' && (
                <div className="space-y-4">
                  <Document
                    file={previewUrl}
                    onLoadSuccess={({ numPages }) => setNumPages(numPages)}
                    className="flex justify-center"
                  >
                    <Page pageNumber={pageNumber} className="max-w-full" />
                  </Document>

                  {numPages > 1 && (
                    <div className="flex items-center justify-center gap-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPageNumber((p) => Math.max(1, p - 1))}
                        disabled={pageNumber <= 1}
                      >
                        <ChevronLeft className="h-4 w-4" />
                      </Button>
                      <span className="text-sm text-muted-foreground">
                        Pagina {pageNumber} van {numPages}
                      </span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPageNumber((p) => Math.min(numPages, p + 1))}
                        disabled={pageNumber >= numPages}
                      >
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>
              )}

              {/* DOCX */}
              {(file.mime_type.includes('word') ||
                file.mime_type.includes('openxmlformats')) && (
                <div>
                  {docxError ? (
                    <div className="flex items-center gap-2 p-4 text-sm text-muted-foreground">
                      <AlertCircle className="h-5 w-5" />
                      <span>Fout bij laden van document. Download het bestand om te bekijken.</span>
                    </div>
                  ) : (
                    <div ref={docxContainerRef} className="docx-preview max-w-full overflow-auto" />
                  )}
                </div>
              )}

              {/* Fallback */}
              {!file.mime_type.startsWith('image/') &&
                file.mime_type !== 'application/pdf' &&
                !file.mime_type.includes('word') &&
                !file.mime_type.includes('openxmlformats') && (
                  <div className="text-center py-8 text-muted-foreground">
                    <p>Voorbeeld niet beschikbaar voor dit bestandstype</p>
                    <Button variant="link" onClick={handleDownload} className="mt-2">
                      Download bestand
                    </Button>
                  </div>
                )}
            </div>

            {/* Metadata */}
            <div className="space-y-3">
              <h3 className="font-semibold text-sm">Metadata</h3>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <p className="text-muted-foreground">Type</p>
                  <p className="font-medium">{getMimeTypeLabel(file.mime_type)}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Grootte</p>
                  <p className="font-medium">{formatBytes(file.size_bytes)}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Geüpload op</p>
                  <p className="font-medium">{formatDate(file.uploaded_at)}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Map</p>
                  <p className="font-medium">{getFolderName()}</p>
                </div>
              </div>
              {file.overrides_file_id && (
                <Badge variant="outline" className="mt-2">
                  Overschrijft gedeeld bestand
                </Badge>
              )}
            </div>

            {/* File Actions */}
            <FileActions
              file={file}
              folders={folders}
              onRename={handleRename}
              onMove={handleMove}
              onReplace={handleReplace}
              onDelete={() => setDeleteDialogOpen(true)}
              onDownload={handleDownload}
              readOnly={readOnly}
            />
          </div>
        </SheetContent>
      </Sheet>

      {/* Delete Confirmation */}
      <DeleteConfirmation
        file={file}
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onConfirm={handleDelete}
      />
    </>
  )
}
