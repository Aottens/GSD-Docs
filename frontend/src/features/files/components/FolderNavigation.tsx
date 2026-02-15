import { useState } from 'react'
import { FolderOpen, Plus, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import type { FolderInfo } from '../types/file'

interface FolderNavigationProps {
  folders: FolderInfo[]
  currentFolderId: number | null
  onFolderChange: (folderId: number | null) => void
  onCreateFolder?: (name: string) => void
}

export function FolderNavigation({
  folders,
  currentFolderId,
  onFolderChange,
  onCreateFolder,
}: FolderNavigationProps) {
  const [isCreating, setIsCreating] = useState(false)
  const [newFolderName, setNewFolderName] = useState('')

  // Build breadcrumb path
  const buildPath = (): FolderInfo[] => {
    if (!currentFolderId) return []

    const path: FolderInfo[] = []
    let current = folders.find((f) => f.id === currentFolderId)

    while (current) {
      path.unshift(current)
      current = current.parent_id ? folders.find((f) => f.id === current!.parent_id) : undefined
    }

    return path
  }

  const breadcrumbPath = buildPath()

  // Get subfolders at current level
  const subfolders = folders.filter((f) => f.parent_id === currentFolderId)

  const handleCreateFolder = () => {
    if (newFolderName.trim() && onCreateFolder) {
      onCreateFolder(newFolderName.trim())
      setNewFolderName('')
      setIsCreating(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <button
          onClick={() => onFolderChange(null)}
          className="hover:text-foreground transition-colors"
        >
          Root
        </button>
        {breadcrumbPath.map((folder) => (
          <div key={folder.id} className="flex items-center gap-2">
            <ChevronRight className="h-4 w-4" />
            <button
              onClick={() => onFolderChange(folder.id)}
              className="hover:text-foreground transition-colors"
            >
              {folder.name}
            </button>
          </div>
        ))}
      </div>

      {/* Subfolders Grid */}
      {subfolders.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {subfolders.map((folder) => (
            <button
              key={folder.id}
              onClick={() => onFolderChange(folder.id)}
              className="flex items-center gap-2 p-3 border rounded-lg hover:bg-muted/50 transition-colors text-left"
            >
              <FolderOpen className="h-5 w-5 text-amber-500 shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{folder.name}</p>
                {folder.file_count !== undefined && (
                  <p className="text-xs text-muted-foreground">
                    {folder.file_count} {folder.file_count === 1 ? 'bestand' : 'bestanden'}
                  </p>
                )}
              </div>
            </button>
          ))}
        </div>
      )}

      {/* Create Folder */}
      {onCreateFolder && (
        <div>
          {isCreating ? (
            <div className="flex gap-2">
              <Input
                placeholder="Map naam..."
                value={newFolderName}
                onChange={(e) => setNewFolderName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleCreateFolder()
                  if (e.key === 'Escape') {
                    setIsCreating(false)
                    setNewFolderName('')
                  }
                }}
                autoFocus
              />
              <Button onClick={handleCreateFolder} disabled={!newFolderName.trim()}>
                Aanmaken
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setIsCreating(false)
                  setNewFolderName('')
                }}
              >
                Annuleren
              </Button>
            </div>
          ) : (
            <Button variant="outline" size="sm" onClick={() => setIsCreating(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Nieuwe map
            </Button>
          )}
        </div>
      )}
    </div>
  )
}
