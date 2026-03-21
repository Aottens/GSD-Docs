/**
 * TypeScript interfaces for verification detail and review session.
 * These mirror the backend Pydantic schemas exactly (app/schemas/verification.py).
 */

export interface TruthResult {
  description: string
  status: 'PASS' | 'GAP'
  levels: {
    exists: 'pass' | 'gap' | '-' | 'n/a'
    substantive: 'pass' | 'gap' | '-' | 'n/a'
    complete: 'pass' | 'gap' | '-' | 'n/a'
    consistent: 'pass' | 'gap' | '-' | 'n/a'
    standards: 'pass' | 'gap' | '-' | 'n/a'
  }
  failed_level: string | null
  gap_description: string | null
  evidence_files: string[]
  standards_violations: Array<{ reference: string; text: string }>
}

export interface VerificationDetail {
  has_verification: boolean
  status: string | null          // "PASS" | "GAPS_FOUND" | "GAPS_FOUND (ESCALATED)" | "UNKNOWN"
  current_cycle: number
  max_cycles: number
  is_blocked: boolean
  truths: TruthResult[]
  total_truths: number
  passed_count: number
  gap_count: number
}

export interface SectionReview {
  sectionId: string
  status: 'goedgekeurd' | 'opmerking' | 'afgewezen'
  feedback: string              // empty string for goedgekeurd
  timestamp: number
}

export interface ReviewContextValue {
  reviews: Record<string, SectionReview>
  setReview: (sectionId: string, status: SectionReview['status'], feedback: string) => void
  clearReviews: () => void
  exportAsJson: () => string
  reviewedCount: number
}
