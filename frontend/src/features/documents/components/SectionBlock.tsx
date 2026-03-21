import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import { useSectionContent } from '../hooks/useSectionContent'
import { MermaidDiagram } from './MermaidDiagram'
import { PlanCard } from './PlanCard'
import { EmptySectionCard } from './EmptySectionCard'
import type { OutlineNode } from '../types/document'
import type { Components } from 'react-markdown'

function getWaveColor(wave: number): string {
  if (wave === 1) return 'bg-blue-500/10 text-blue-500 border-blue-500/20'
  if (wave === 2) return 'bg-green-500/10 text-green-500 border-green-500/20'
  if (wave === 3) return 'bg-amber-500/10 text-amber-500 border-amber-500/20'
  return 'bg-purple-500/10 text-purple-500 border-purple-500/20'
}

const markdownComponents: Components = {
  h1: ({ children }) => (
    <h1 className="text-3xl font-semibold leading-[1.2] mt-8 mb-4">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-2xl font-semibold leading-[1.2] mt-6 mb-3">{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-2xl font-semibold leading-[1.2] mt-4 mb-2">{children}</h3>
  ),
  p: ({ children }) => (
    <p className="text-base leading-[1.7] mb-4">{children}</p>
  ),
  table: ({ children }) => (
    <table className="w-full border-collapse text-sm mb-4">{children}</table>
  ),
  th: ({ children }) => (
    <th className="border border-border bg-muted px-3 py-2 text-left text-sm font-semibold">{children}</th>
  ),
  td: ({ children }) => (
    <td className="border border-border px-3 py-2 text-sm">{children}</td>
  ),
  code: ({ className, children, ...props }) => {
    const lang = /language-(\w+)/.exec(className || '')?.[1]
    if (lang === 'mermaid') {
      return <MermaidDiagram chart={String(children).replace(/\n$/, '')} />
    }
    // Check if inline by looking at parent context (no className = inline)
    if (!className) {
      return (
        <code className="bg-muted rounded px-1.5 py-0.5 text-sm" {...props}>
          {children}
        </code>
      )
    }
    return (
      <pre className="bg-muted rounded p-4 overflow-x-auto mb-4">
        <code className="text-sm" {...props}>{children}</code>
      </pre>
    )
  },
  ul: ({ children }) => (
    <ul className="list-disc pl-6 mb-4 space-y-1">{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="list-decimal pl-6 mb-4 space-y-1">{children}</ol>
  ),
  li: ({ children }) => (
    <li className="text-base leading-[1.7]">{children}</li>
  ),
  blockquote: ({ children }) => (
    <blockquote className="border-l-4 border-border pl-4 italic text-muted-foreground mb-4">
      {children}
    </blockquote>
  ),
}

interface SectionBlockProps {
  node: OutlineNode
  language: 'nl' | 'en'
  projectId: number
  depth?: number
}

function SectionContent({
  node,
  language,
  projectId,
}: {
  node: OutlineNode
  language: 'nl' | 'en'
  projectId: number
}) {
  const isWritten = node.status === 'written' || node.status === 'verified'
  const { data, isLoading, error } = useSectionContent(projectId, node.id, isWritten && node.has_content)

  if (isWritten) {
    if (isLoading) return <Skeleton className="h-48 w-full" />
    if (error) {
      return (
        <p className="text-sm text-muted-foreground">
          Sectie-inhoud kon niet worden geladen. Ververs de pagina of controleer de verbinding met de server.
        </p>
      )
    }
    if (data?.markdown_content) {
      return (
        <div className="prose-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
            {data.markdown_content}
          </ReactMarkdown>
        </div>
      )
    }
    return null
  }

  if (node.status === 'planned' && node.plan_info) {
    const cliCommand = `/doc:write-phase`
    return (
      <div className="space-y-4">
        <PlanCard planInfo={node.plan_info} sectionTitle={node.title[language]} />
        <EmptySectionCard
          sectionId={node.id}
          sectionTitle={node.title[language]}
          status="planned"
          cliCommand={cliCommand}
        />
      </div>
    )
  }

  // status === 'empty'
  const cliCommand = `/doc:plan-phase`
  return (
    <EmptySectionCard
      sectionId={node.id}
      sectionTitle={node.title[language]}
      status="empty"
      cliCommand={cliCommand}
    />
  )
}

export function SectionBlock({ node, language, projectId, depth = 1 }: SectionBlockProps) {
  const title = node.title[language]

  return (
    <div id={`section-${node.id}`} className="mb-8">
      {depth === 1 && <Separator className="mb-6" />}

      {/* Section header */}
      <div className={cn('flex items-center gap-3 mb-4', depth === 1 ? 'mb-6' : 'mb-4')}>
        <span className="bg-muted text-muted-foreground rounded text-sm px-1.5 py-0.5 shrink-0">
          {node.id}
        </span>
        {depth === 1 ? (
          <h2 className="text-2xl font-semibold leading-[1.2]">{title}</h2>
        ) : (
          <h3 className="text-xl font-semibold leading-[1.2]">{title}</h3>
        )}
        {node.has_plan && node.plan_info && (
          <Badge
            variant="outline"
            className={cn('text-xs shrink-0', getWaveColor(node.plan_info.wave))}
          >
            G{node.plan_info.wave}
          </Badge>
        )}
      </div>

      {/* Content — only render for leaf nodes or nodes without children */}
      {node.children.length === 0 && (
        <SectionContent node={node} language={language} projectId={projectId} />
      )}

      {/* Children */}
      {node.children.map(child => (
        <SectionBlock
          key={child.id}
          node={child}
          language={language}
          projectId={projectId}
          depth={depth + 1}
        />
      ))}
    </div>
  )
}
