export interface NavigationItem {
  id: string
  label: string
  icon: string
  path?: string
  children?: NavigationItem[]
}

export interface QuickAction {
  id: string
  label: string
  icon: string
  description: string
  disabled: boolean
  comingSoon?: string
}
