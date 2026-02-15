import { useState } from 'react'
import { Search } from 'lucide-react'
import { Input } from '@/components/ui/input'
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
import { useFileUpload } from '../hooks/useFileUpload'
import { useProjectFiles, useProjectFolders, useCreateFolder } from '../hooks/useFiles'

interface ProjectFilesTabProps {
  projectId: number
}

export function ProjectFilesTab({ projectId }: ProjectFilesTabProps) {
  const [currentFolderId, setCurrentFolderId] = useState<number | null>(null)
  const [search, setSearch] = useState('')
  const [fileType, setFileType] = useState<string | undefined>(undefined)

  // Queries
  const { data: filesData, refetch: refetchFiles } = useProjectFiles(
    projectId,
    currentFolderId || undefined,
    fileType,
    search || undefined
  )
  const { data: folders = [] } = useProjectFolders(projectId)

  // Mutations
  const createFolderMutation = useCreateFolder(projectId)

  // File upload
  const { uploadFiles, progressMap, isUploading } = useFileUpload({
    projectId,
    onUploadComplete: () => {
      refetchFiles()
    },
  })

  const handleFilesSelected = (files: File[]) => {
    uploadFiles(files, currentFolderId || undefined)
  }

  const handleCreateFolder = (name: string) => {
    createFolderMutation.mutate({
      name,
      parentId: currentFolderId || undefined,
    })
  }

  const handleFileClick = (_file: any) => {
    // TODO: Open FilePreviewPanel in Task 2
  }

  return (
    <div className="space-y-6">
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
    </div>
  )
}
