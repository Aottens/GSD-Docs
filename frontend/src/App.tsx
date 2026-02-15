import { useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { queryClient } from '@/lib/queryClient'
import { useThemeStore } from '@/stores/themeStore'
import { Header } from '@/components/layout/Header'
import { Dashboard } from '@/features/dashboard/Dashboard'
import { ProjectWizard } from '@/features/wizard/ProjectWizard'

// Placeholder component for future implementation
function ProjectWorkspace() {
  return (
    <div className="container py-6">
      <h1 className="text-3xl font-bold">Project Workspace</h1>
      <p className="text-muted-foreground mt-2">Project workspace will be implemented shortly.</p>
    </div>
  )
}

function App() {
  const { theme, setTheme } = useThemeStore()

  // Initialize theme on mount
  useEffect(() => {
    setTheme(theme)
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-background">
          <Header />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/projects/new" element={<ProjectWizard />} />
            <Route path="/projects/:id" element={<ProjectWorkspace />} />
          </Routes>
        </div>
      </BrowserRouter>
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  )
}

export default App
