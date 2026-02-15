import { useState, useEffect } from 'react'
import { Search } from 'lucide-react'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'
import type { DashboardTab, SortOption, FilterState } from '../types'

interface DashboardFiltersProps {
  filters: FilterState
  onFiltersChange: (filters: FilterState) => void
}

const sortOptions: { value: SortOption; label: string }[] = [
  { value: 'updated_at', label: 'Most Recent' },
  { value: 'name', label: 'Name A-Z' },
  { value: 'type', label: 'Type' },
  { value: 'created_at', label: 'Created Date' },
]

export function DashboardFilters({ filters, onFiltersChange }: DashboardFiltersProps) {
  const [searchValue, setSearchValue] = useState(filters.search)

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchValue !== filters.search) {
        onFiltersChange({ ...filters, search: searchValue })
      }
    }, 300)

    return () => clearTimeout(timer)
  }, [searchValue])

  const handleTabChange = (value: string) => {
    onFiltersChange({ ...filters, tab: value as DashboardTab })
  }

  const handleSortChange = (sortBy: SortOption) => {
    // Toggle sort order if clicking same option
    const sortOrder =
      filters.sortBy === sortBy && filters.sortOrder === 'asc' ? 'desc' : 'asc'
    onFiltersChange({ ...filters, sortBy, sortOrder })
  }

  const currentSortLabel =
    sortOptions.find((opt) => opt.value === filters.sortBy)?.label || 'Sort'

  return (
    <div className="space-y-4">
      <Tabs value={filters.tab} onValueChange={handleTabChange}>
        <TabsList>
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="active">Active</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
        </TabsList>
      </Tabs>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search projects..."
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="pl-9"
          />
        </div>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="sm:w-auto w-full">
              {currentSortLabel}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {sortOptions.map((option) => (
              <DropdownMenuItem
                key={option.value}
                onClick={() => handleSortChange(option.value)}
              >
                {option.label}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  )
}
