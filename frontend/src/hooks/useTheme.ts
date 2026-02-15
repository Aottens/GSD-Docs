import { useThemeStore } from '@/stores/themeStore'

export const useTheme = () => {
  const { theme, setTheme } = useThemeStore()
  return { theme, setTheme }
}
