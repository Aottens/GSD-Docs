import { Download } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { useExportVersions } from '../hooks/useExportApi'
import type { ExportVersion } from '@/types/export'

interface VersionHistoryProps {
  projectId: number
}

function formatDate(isoString: string): string {
  const date = new Date(isoString)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${day}-${month}-${year} ${hours}:${minutes}`
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function VersionTypeBadge({ version }: { version: ExportVersion }) {
  if (version.mode === 'draft') {
    return (
      <Badge variant="outline" className="text-amber-500 border-amber-500/30">
        Concept
      </Badge>
    )
  }
  return (
    <Badge variant="outline" className="text-green-500 border-green-500/30">
      Definitief
    </Badge>
  )
}

export function VersionHistory({ projectId }: VersionHistoryProps) {
  const { data, isLoading } = useExportVersions(projectId)

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-xl font-semibold">Versiegeschiedenis</h2>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Versie</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Taal</TableHead>
            <TableHead>Datum</TableHead>
            <TableHead>Grootte</TableHead>
            <TableHead>Downloaden</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading && (
            <>
              {[0, 1, 2].map(i => (
                <TableRow key={i}>
                  <TableCell colSpan={6}>
                    <Skeleton className="h-9 w-full" />
                  </TableCell>
                </TableRow>
              ))}
            </>
          )}
          {!isLoading && (!data?.versions || data.versions.length === 0) && (
            <TableRow>
              <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                Nog geen exports. Gebruik de pijplijn hierboven om uw eerste document te exporteren.
              </TableCell>
            </TableRow>
          )}
          {!isLoading &&
            data?.versions?.map(version => (
              <TableRow key={version.filename}>
                <TableCell className="font-mono text-sm">{version.version}</TableCell>
                <TableCell>
                  <VersionTypeBadge version={version} />
                </TableCell>
                <TableCell className="uppercase text-sm">{version.language}</TableCell>
                <TableCell className="text-sm">{formatDate(version.created_at)}</TableCell>
                <TableCell className="text-sm">{formatBytes(version.size_bytes)}</TableCell>
                <TableCell>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() =>
                      window.open(
                        `/api/projects/${projectId}/export/download/${version.filename}`
                      )
                    }
                  >
                    <Download className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
        </TableBody>
      </Table>
    </div>
  )
}
