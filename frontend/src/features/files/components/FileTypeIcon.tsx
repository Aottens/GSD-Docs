import { ImageIcon, FileText, File } from 'lucide-react'
import { cn } from '@/lib/utils'

interface FileTypeIconProps {
  mimeType: string
  className?: string
}

export function FileTypeIcon({ mimeType, className }: FileTypeIconProps) {
  // Images
  if (mimeType.startsWith('image/')) {
    return <ImageIcon className={cn('h-4 w-4 text-blue-500', className)} />
  }

  // PDF
  if (mimeType === 'application/pdf') {
    return <FileText className={cn('h-4 w-4 text-red-500', className)} />
  }

  // Word documents
  if (
    mimeType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
    mimeType === 'application/msword'
  ) {
    return <FileText className={cn('h-4 w-4 text-blue-600', className)} />
  }

  // Default
  return <File className={cn('h-4 w-4 text-gray-500', className)} />
}
