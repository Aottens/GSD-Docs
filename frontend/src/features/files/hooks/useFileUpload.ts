import { useState, useCallback } from 'react'
import type { UploadProgress, UploadStatus } from '../types/file'

interface UseFileUploadOptions {
  projectId?: number
  onUploadComplete?: () => void
}

export function useFileUpload({ projectId, onUploadComplete }: UseFileUploadOptions = {}) {
  const [progressMap, setProgressMap] = useState<Map<string, UploadProgress>>(new Map())
  const [isUploading, setIsUploading] = useState(false)

  const uploadFile = useCallback(
    (file: File, folderId?: number, docType?: string): Promise<void> => {
      return new Promise((resolve, reject) => {
        const formData = new FormData()
        formData.append('file', file)

        // Build URL with query params if provided
        const baseUrl = projectId
          ? `/api/projects/${projectId}/files`
          : '/api/files/shared'
        const params = new URLSearchParams()
        if (folderId) params.set('folder_id', String(folderId))
        if (docType) params.set('doc_type', docType)
        const queryString = params.toString()
        const url = queryString ? `${baseUrl}?${queryString}` : baseUrl

        const xhr = new XMLHttpRequest()

        // Track upload progress
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            const progress = Math.round((e.loaded / e.total) * 100)
            setProgressMap((prev) => {
              const newMap = new Map(prev)
              newMap.set(file.name, {
                file,
                progress,
                status: 'uploading' as UploadStatus,
              })
              return newMap
            })
          }
        })

        // Handle completion
        xhr.addEventListener('load', () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            setProgressMap((prev) => {
              const newMap = new Map(prev)
              newMap.set(file.name, {
                file,
                progress: 100,
                status: 'done' as UploadStatus,
              })
              return newMap
            })
            resolve()
          } else {
            // Parse error response
            let errorMessage = 'Upload mislukt'
            try {
              const errorData = JSON.parse(xhr.responseText)
              errorMessage = errorData.detail || errorMessage
            } catch {
              errorMessage = xhr.statusText || errorMessage
            }

            setProgressMap((prev) => {
              const newMap = new Map(prev)
              newMap.set(file.name, {
                file,
                progress: 0,
                status: 'error' as UploadStatus,
                error: errorMessage,
              })
              return newMap
            })
            reject(new Error(errorMessage))
          }
        })

        // Handle network errors
        xhr.addEventListener('error', () => {
          setProgressMap((prev) => {
            const newMap = new Map(prev)
            newMap.set(file.name, {
              file,
              progress: 0,
              status: 'error' as UploadStatus,
              error: 'Netwerkfout',
            })
            return newMap
          })
          reject(new Error('Netwerkfout'))
        })

        xhr.open('POST', url)
        xhr.send(formData)
      })
    },
    [projectId]
  )

  const uploadFiles = useCallback(
    async (files: File[], folderId?: number, docType?: string) => {
      setIsUploading(true)

      // Initialize all files as pending
      setProgressMap((prev) => {
        const newMap = new Map(prev)
        files.forEach((file) => {
          newMap.set(file.name, {
            file,
            progress: 0,
            status: 'pending' as UploadStatus,
          })
        })
        return newMap
      })

      // Upload sequentially to avoid overwhelming server
      for (const file of files) {
        try {
          await uploadFile(file, folderId, docType)
        } catch (error) {
          console.error(`Failed to upload ${file.name}:`, error)
          // Continue with next file even if one fails
        }
      }

      setIsUploading(false)
      onUploadComplete?.()
    },
    [uploadFile, onUploadComplete]
  )

  const clearProgress = useCallback(() => {
    setProgressMap(new Map())
  }, [])

  return {
    uploadFile,
    uploadFiles,
    progressMap,
    isUploading,
    clearProgress,
  }
}
