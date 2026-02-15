import { useState, useRef } from 'react'
import { Search } from 'lucide-react'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { FolderNavigation } from './FolderNavigation'
import { FileList } from './FileList'
import { FilePreviewPanel } from './FilePreviewPanel'
import { useSharedFiles, useSharedFolders, useOverrideFile } from '../hooks/useFiles'
import type { FileMetadata } from '../types/file'

interface SharedLibraryTabProps {
  projectId: number
}

export function SharedLibraryTab({ projectId }: SharedLibraryTabProps) {
  const [currentFolderId, setCurrentFolderId] = useState<number | null>(null)
  const [search, setSearch] = useState('')
  const [fileType, setFileType] = useState<string | undefined>(undefined)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedSharedFileId, setSelectedSharedFileId] = useState<number | null>(null)
  const [selectedFile, setSelectedFile] = useState<FileMetadata | null>(null)
  const [previewOpen, setPreviewOpen] = useState(false)

  // Queries
  const { data: filesData } = useSharedFiles(
    currentFolderId || undefined,
    fileType,
    search || undefined
  )
  const { data: folders = [] } = useSharedFolders()

  // Mutations
  const overrideMutation = useOverrideFile(projectId)

  const handleOverride = (file: FileMetadata) => {
    setSelectedSharedFileId(file.id)
    fileInputRef.current?.click()
  }

  const handleFileSelected = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file && selectedSharedFileId) {
      overrideMutation.mutate({
        fileId: selectedSharedFileId,
        newFile: file,
      })
      setSelectedSharedFileId(null)
    }
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleFileClick = (file: FileMetadata) => {
    setSelectedFile(file)
    setPreviewOpen(true)
  }

  return (
    <div className="space-y-6">
      {/* Hidden file input for override action */}
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept=".pdf,.docx,.doc,.png,.jpg,.jpeg"
        onChange={handleFileSelected}
      />

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

      {/* Folder Navigation (read-only: no create folder) */}
      <FolderNavigation
        folders={folders}
        currentFolderId={currentFolderId}
        onFolderChange={setCurrentFolderId}
      />

      {/* File List with Override Action */}
      <FileList
        files={filesData?.files || []}
        onFileClick={handleFileClick}
        showOverrideAction={true}
        onOverride={handleOverride}
      />

      {/* File Preview Panel (read-only for shared library) */}
      <FilePreviewPanel
        file={selectedFile}
        open={previewOpen}
        onOpenChange={setPreviewOpen}
        folders={folders}
        onFileUpdated={() => {}} // No updates needed for shared library
        readOnly={true}
      />
    </div>
  )
}
