import { Loader2 } from 'lucide-react'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import type { FileMetadata } from '../types/file'

interface DeleteConfirmationProps {
  file: FileMetadata | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirm: () => void
  isDeleting?: boolean
}

export function DeleteConfirmation({
  file,
  open,
  onOpenChange,
  onConfirm,
  isDeleting = false,
}: DeleteConfirmationProps) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Bestand verwijderen?</AlertDialogTitle>
          <AlertDialogDescription>
            Weet je zeker dat je &ldquo;{file?.original_filename}&rdquo; wilt verwijderen? Deze
            actie kan niet ongedaan worden gemaakt.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isDeleting}>Annuleren</AlertDialogCancel>
          <AlertDialogAction
            onClick={(e) => {
              e.preventDefault()
              onConfirm()
            }}
            disabled={isDeleting}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            {isDeleting && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
            {isDeleting ? 'Verwijderen...' : 'Verwijderen'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
