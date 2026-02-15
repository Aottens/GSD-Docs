import { useState, useRef } from 'react'
import { Download, Pencil, FolderInput, RefreshCw, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { FileMetadata, FolderInfo } from '../types/file'

interface FileActionsProps {
  file: FileMetadata
  folders: FolderInfo[]
  onRename: (newName: string) => void
  onMove: (folderId: number | null) => void
  onReplace: (newFile: File) => void
  onDelete: () => void
  onDownload: () => void
  readOnly?: boolean
}

export function FileActions({
  file,
  folders,
  onRename,
  onMove,
  onReplace,
  onDelete,
  onDownload,
  readOnly = false,
}: FileActionsProps) {
  const [isRenaming, setIsRenaming] = useState(false)
  const [newName, setNewName] = useState(file.original_filename)
  const [isMoving, setIsMoving] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleRename = () => {
    if (newName.trim() && newName !== file.original_filename) {
      onRename(newName.trim())
      setIsRenaming(false)
    }
  }

  const handleMove = (folderId: string) => {
    const targetId = folderId === 'root' ? null : parseInt(folderId, 10)
    onMove(targetId)
    setIsMoving(false)
  }

  const handleReplaceClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileSelected = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0]
    if (selectedFile) {
      onReplace(selectedFile)
    }
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="space-y-4">
      {/* Hidden file input for replace */}
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept=".pdf,.docx,.doc,.png,.jpg,.jpeg"
        onChange={handleFileSelected}
      />

      {/* Rename Section */}
      {!readOnly && (
        <div>
          {isRenaming ? (
            <div className="flex gap-2">
              <Input
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleRename()
                  if (e.key === 'Escape') setIsRenaming(false)
                }}
                autoFocus
              />
              <Button onClick={handleRename} size="sm">
                OK
              </Button>
              <Button variant="outline" onClick={() => setIsRenaming(false)} size="sm">
                Annuleren
              </Button>
            </div>
          ) : null}
        </div>
      )}

      {/* Move Section */}
      {!readOnly && (
        <div>
          {isMoving ? (
            <div className="flex gap-2">
              <Select
                value={file.folder_id?.toString() || 'root'}
                onValueChange={handleMove}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="root">Root</SelectItem>
                  {folders.map((folder) => (
                    <SelectItem key={folder.id} value={folder.id.toString()}>
                      {folder.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button variant="outline" onClick={() => setIsMoving(false)} size="sm">
                Annuleren
              </Button>
            </div>
          ) : null}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-2">
        <Button variant="outline" size="sm" onClick={onDownload}>
          <Download className="h-4 w-4 mr-2" />
          Downloaden
        </Button>

        {!readOnly && (
          <>
            <Button variant="outline" size="sm" onClick={() => setIsRenaming(true)}>
              <Pencil className="h-4 w-4 mr-2" />
              Hernoemen
            </Button>

            <Button variant="outline" size="sm" onClick={() => setIsMoving(true)}>
              <FolderInput className="h-4 w-4 mr-2" />
              Verplaatsen
            </Button>

            <Button variant="outline" size="sm" onClick={handleReplaceClick}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Vervangen
            </Button>

            <Button variant="destructive" size="sm" onClick={onDelete}>
              <Trash2 className="h-4 w-4 mr-2" />
              Verwijderen
            </Button>
          </>
        )}
      </div>
    </div>
  )
}
