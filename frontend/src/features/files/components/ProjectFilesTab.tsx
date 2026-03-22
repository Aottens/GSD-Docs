import { useState } from 'react'
import { Search } from 'lucide-react'
import { useQueryClient } from '@tanstack/react-query'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { FileUploadZone } from './FileUploadZone'
import { FolderNavigation } from './FolderNavigation'
import { FileList } from './FileList'
import { FilePreviewPanel } from './FilePreviewPanel'
import { DocCoverageSection } from './DocCoverageSection'
import { useFileUpload } from '../hooks/useFileUpload'
import { useProjectFiles, useProjectFolders, useCreateFolder } from '../hooks/useFiles'
import { useDocTypeConfig } from '@/features/projects/hooks/useSetupState'
import type { FileMetadata } from '../types/file'

interface ProjectFilesTabProps {
  projectId: number
  projectType?: string
}

export function ProjectFilesTab({ projectId, projectType }: ProjectFilesTabProps) {
  const [currentFolderId, setCurrentFolderId] = useState<number | null>(null)
  const [search, setSearch] = useState('')
  const [fileType, setFileType] = useState<string | undefined>(undefined)
  const [selectedFile, setSelectedFile] = useState<FileMetadata | null>(null)
  const [previewOpen, setPreviewOpen] = useState(false)

  // Doc-type upload prompt state
  const [pendingUploadFiles, setPendingUploadFiles] = useState<File[]>([])
  const [pendingDocType, setPendingDocType] = useState<string>('')
  const [showDocTypePrompt, setShowDocTypePrompt] = useState(false)

  const queryClient = useQueryClient()

  // Queries
  const { data: filesData, refetch: refetchFiles } = useProjectFiles(
    projectId,
    currentFolderId || undefined,
    fileType,
    search || undefined
  )
  const { data: folders = [] } = useProjectFolders(projectId)
  const { data: docTypes } = useDocTypeConfig(projectType)

  // Mutations
  const createFolderMutation = useCreateFolder(projectId)

  // File upload
  const { uploadFiles, progressMap, isUploading } = useFileUpload({
    projectId,
    onUploadComplete: () => {
      refetchFiles()
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'setup-state'] })
    },
  })

  const handleFilesSelected = (files: File[]) => {
    if (docTypes && docTypes.length > 0) {
      setPendingUploadFiles(files)
      setShowDocTypePrompt(true)
    } else {
      // No doc types configured — upload without classification
      uploadFiles(files, currentFolderId || undefined)
    }
  }

  const handleDocTypeConfirm = () => {
    uploadFiles(pendingUploadFiles, currentFolderId || undefined, pendingDocType || undefined)
    setPendingUploadFiles([])
    setPendingDocType('')
    setShowDocTypePrompt(false)
  }

  const handleDocTypeSkip = () => {
    // Upload without doc_type
    uploadFiles(pendingUploadFiles, currentFolderId || undefined)
    setPendingUploadFiles([])
    setPendingDocType('')
    setShowDocTypePrompt(false)
  }

  const handleCreateFolder = (name: string) => {
    createFolderMutation.mutate({
      name,
      parentId: currentFolderId || undefined,
    })
  }

  const handleFileClick = (file: FileMetadata) => {
    setSelectedFile(file)
    setPreviewOpen(true)
  }

  return (
    <div className="space-y-6">
      {/* Document Coverage */}
      {projectType && <DocCoverageSection projectId={projectId} />}

      {/* Doc-type upload prompt */}
      {showDocTypePrompt && (
        <Card className="p-4 space-y-3">
          <p className="text-sm font-medium">Documenttype</p>
          <Select value={pendingDocType} onValueChange={setPendingDocType}>
            <SelectTrigger>
              <SelectValue placeholder="Selecteer type..." />
            </SelectTrigger>
            <SelectContent>
              {docTypes?.map((dt) => (
                <SelectItem key={dt.id} value={dt.id}>
                  {dt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <div className="flex gap-2">
            <Button size="sm" onClick={handleDocTypeConfirm}>
              Uploaden
            </Button>
            <Button size="sm" variant="ghost" onClick={handleDocTypeSkip}>
              Zonder type
            </Button>
          </div>
        </Card>
      )}

      {/* Search and Filter */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Zoeken in bestanden..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={fileType || 'all'} onValueChange={(v) => setFileType(v === 'all' ? undefined : v)}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Alle types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle types</SelectItem>
            <SelectItem value="application/pdf">PDF</SelectItem>
            <SelectItem value="application/vnd.openxmlformats-officedocument.wordprocessingml.document">
              DOCX
            </SelectItem>
            <SelectItem value="image">Afbeeldingen</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Upload Zone */}
      <FileUploadZone
        onFilesSelected={handleFilesSelected}
        disabled={isUploading}
        progressMap={progressMap}
      />

      {/* Folder Navigation */}
      <FolderNavigation
        folders={folders}
        currentFolderId={currentFolderId}
        onFolderChange={setCurrentFolderId}
        onCreateFolder={handleCreateFolder}
      />

      {/* File List */}
      <FileList
        files={filesData?.files || []}
        onFileClick={handleFileClick}
      />

      {/* File Preview Panel */}
      <FilePreviewPanel
        file={selectedFile}
        open={previewOpen}
        onOpenChange={setPreviewOpen}
        folders={folders}
        onFileUpdated={refetchFiles}
      />
    </div>
  )
}
