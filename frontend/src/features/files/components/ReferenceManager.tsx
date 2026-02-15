import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ProjectFilesTab } from './ProjectFilesTab'
import { SharedLibraryTab } from './SharedLibraryTab'

interface ReferenceManagerProps {
  projectId: number
}

export function ReferenceManager({ projectId }: ReferenceManagerProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold mb-2">Referenties</h2>
        <p className="text-sm text-muted-foreground">
          Beheer projectbestanden en toegang tot de gedeelde bibliotheek
        </p>
      </div>

      <Tabs defaultValue="project" className="w-full">
        <TabsList>
          <TabsTrigger value="project">Project bestanden</TabsTrigger>
          <TabsTrigger value="shared">Gedeelde bibliotheek</TabsTrigger>
        </TabsList>

        <TabsContent value="project" className="mt-6">
          <ProjectFilesTab projectId={projectId} />
        </TabsContent>

        <TabsContent value="shared" className="mt-6">
          <SharedLibraryTab projectId={projectId} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
