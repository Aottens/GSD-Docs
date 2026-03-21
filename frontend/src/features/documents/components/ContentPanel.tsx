import { SectionBlock } from './SectionBlock'
import { ReviewSummary } from './ReviewSummary'
import type { OutlineNode } from '../types/document'
import type { VerificationDetail } from '../types/verification'

interface ContentPanelProps {
  sections: OutlineNode[]
  language: 'nl' | 'en'
  projectId: number
  phaseNumber?: number
  phaseHasVerification?: boolean
  verificationData?: VerificationDetail | null
}

function hasNonEmptyNode(nodes: OutlineNode[]): boolean {
  return nodes.some(n => n.status !== 'empty' || hasNonEmptyNode(n.children))
}

export function ContentPanel({ sections, language, projectId, phaseNumber, phaseHasVerification, verificationData }: ContentPanelProps) {
  const hasContent = sections.length > 0 && hasNonEmptyNode(sections)

  return (
    <div className="h-full overflow-auto">
      <div className="max-w-[720px] mx-auto px-6 py-8">
        {sections.length === 0 || !hasContent ? (
          <div className="text-center py-16">
            <h3 className="text-2xl font-semibold mb-2">Nog geen inhoud</h3>
            <p className="text-base text-muted-foreground">
              Dit project heeft nog geen gegenereerde secties. Voer `/doc:plan-phase` uit in de CLI om te beginnen.
            </p>
          </div>
        ) : (
          sections.map(section => (
            <SectionBlock
              key={section.id}
              node={section}
              language={language}
              projectId={projectId}
              phaseNumber={phaseNumber}
              phaseHasVerification={phaseHasVerification}
              verificationData={verificationData}
              depth={1}
            />
          ))
        )}
        {phaseHasVerification && phaseNumber && (
          <ReviewSummary phaseNumber={phaseNumber} />
        )}
      </div>
    </div>
  )
}
