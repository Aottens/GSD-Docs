export type DashboardTab = 'active' | 'completed' | 'all'

export type SortOption = 'updated_at' | 'name' | 'type' | 'created_at'

export interface FilterState {
  tab: DashboardTab
  search: string
  sortBy: SortOption
  sortOrder: 'asc' | 'desc'
}
