import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import type { TypicalMatch } from '@/types/sds'
import { TypicalMatchDetail } from './TypicalMatchDetail'

interface TypicalsMatchTableProps {
  matches: TypicalMatch[]
}

type SortColumn = 'equipment_module' | 'matched_typical' | 'confidence' | 'status'
type SortDirection = 'asc' | 'desc'

function getConfidenceClass(confidence: number): string {
  if (confidence >= 70) return 'text-green-500'
  if (confidence >= 40) return 'text-amber-500'
  return 'text-red-500'
}

function StatusBadge({ status }: { status: TypicalMatch['status'] }) {
  if (status === 'matched') {
    return (
      <Badge className="bg-green-500/10 text-green-500 border-green-500/20">
        Gekoppeld
      </Badge>
    )
  }
  if (status === 'low_confidence') {
    return (
      <Badge className="bg-amber-500/10 text-amber-500 border-amber-500/20">
        Lage overeenkomst
      </Badge>
    )
  }
  return <Badge variant="destructive">NIEUW TYPICAL NODIG</Badge>
}

export function TypicalsMatchTable({ matches }: TypicalsMatchTableProps) {
  const [filter, setFilter] = useState('')
  const [sortColumn, setSortColumn] = useState<SortColumn>('equipment_module')
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')
  const [expandedRow, setExpandedRow] = useState<string | null>(null)

  const handleSort = (column: SortColumn) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(column)
      setSortDirection('asc')
    }
  }

  const filtered = matches.filter(m =>
    m.equipment_module.toLowerCase().includes(filter.toLowerCase())
  )

  const sorted = [...filtered].sort((a, b) => {
    let aVal: string | number
    let bVal: string | number

    switch (sortColumn) {
      case 'equipment_module':
        aVal = a.equipment_module
        bVal = b.equipment_module
        break
      case 'matched_typical':
        aVal = a.matched_typical ?? ''
        bVal = b.matched_typical ?? ''
        break
      case 'confidence':
        aVal = a.confidence
        bVal = b.confidence
        break
      case 'status':
        aVal = a.status
        bVal = b.status
        break
    }

    if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1
    if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1
    return 0
  })

  const SortIcon = ({ column }: { column: SortColumn }) => {
    if (sortColumn !== column) return null
    return sortDirection === 'asc' ? (
      <ChevronUp className="inline h-3 w-3 ml-1" />
    ) : (
      <ChevronDown className="inline h-3 w-3 ml-1" />
    )
  }

  return (
    <div className="space-y-3">
      <Input
        placeholder="Filter op module..."
        value={filter}
        onChange={e => setFilter(e.target.value)}
        className="max-w-sm"
      />

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead
              className="cursor-pointer select-none"
              onClick={() => handleSort('equipment_module')}
            >
              Uitrustingsmodule
              <SortIcon column="equipment_module" />
            </TableHead>
            <TableHead
              className="cursor-pointer select-none"
              onClick={() => handleSort('matched_typical')}
            >
              Gekoppeld Typical
              <SortIcon column="matched_typical" />
            </TableHead>
            <TableHead
              className="cursor-pointer select-none"
              onClick={() => handleSort('confidence')}
            >
              Overeenkomst
              <SortIcon column="confidence" />
            </TableHead>
            <TableHead
              className="cursor-pointer select-none"
              onClick={() => handleSort('status')}
            >
              Status
              <SortIcon column="status" />
            </TableHead>
            <TableHead className="w-8" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.map(match => (
            <>
              <TableRow
                key={match.equipment_module}
                className="cursor-pointer min-h-[36px]"
                onClick={() =>
                  setExpandedRow(
                    expandedRow === match.equipment_module
                      ? null
                      : match.equipment_module
                  )
                }
              >
                <TableCell className="font-medium py-2">
                  {match.equipment_module}
                </TableCell>
                <TableCell className="py-2">
                  {match.matched_typical ?? '—'}
                </TableCell>
                <TableCell className="py-2">
                  <span
                    className={`text-sm font-semibold ${getConfidenceClass(match.confidence)}`}
                  >
                    {match.confidence}%
                  </span>
                </TableCell>
                <TableCell className="py-2">
                  <StatusBadge status={match.status} />
                </TableCell>
                <TableCell className="py-2 text-right">
                  {expandedRow === match.equipment_module ? (
                    <ChevronUp className="h-4 w-4 text-muted-foreground" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-muted-foreground" />
                  )}
                </TableCell>
              </TableRow>
              {expandedRow === match.equipment_module && (
                <TableRow key={`${match.equipment_module}-detail`}>
                  <TableCell colSpan={5} className="p-0">
                    <TypicalMatchDetail match={match} />
                  </TableCell>
                </TableRow>
              )}
            </>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
