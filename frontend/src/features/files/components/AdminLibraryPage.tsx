import { useState } from 'react'
import { ArrowLeft, Search } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
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
import { FilePreviewPanel } from './FilePreviewPanel'
import { useFileUpload } from '../hooks/useFileUpload'
import { useSharedFiles, useSharedFolders, useCreateFolder } from '../hooks/useFiles'
import type { FileMetadata } from '../types/file'

export function AdminLibraryPage() {
  const navigate = useNavigate()
  const [currentFolderId, setCurrentFolderId] = useState<number | null>(null)
  const [search, setSearch] = useState('')
  const [fileType, setFileType] = useState<string | undefined>(undefined)
  const [selectedFile, setSelectedFile] = useState<FileMetadata | null>(null)
  const [previewOpen, setPreviewOpen] = useState(false)

  // Queries
  const { data: filesData, refetch: refetchFiles } = useSharedFiles(
    currentFolderId || undefined,
    fileType,
    search || undefined
  )
  const { data: folders = [] } = useSharedFolders()

  // Mutations
  const createFolderMutation = useCreateFolder() // No projectId for shared library

  // File upload (shared library)
  const { uploadFiles, progressMap, isUploading } = useFileUpload({
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

  const handleFileClick = (file: FileMetadata) => {
    setSelectedFile(file)
    setPreviewOpen(true)
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-background sticky top-0 z-10">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => navigate('/')}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Terug naar dashboard
              </Button>
              <div className="h-6 w-px bg-border" />
              <h1 className="text-xl font-semibold">Gedeelde bibliotheek beheren</h1>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="px-6 py-8 max-w-7xl mx-auto">
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
            <Select
              value={fileType || 'all'}
              onValueChange={(v) => setFileType(v === 'all' ? undefined : v)}
            >
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
          <FileList files={filesData?.files || []} onFileClick={handleFileClick} />

          {/* File Preview Panel */}
          <FilePreviewPanel
            file={selectedFile}
            open={previewOpen}
            onOpenChange={setPreviewOpen}
            folders={folders}
            onFileUpdated={refetchFiles}
          />
        </div>
      </main>
    </div>
  )
}
