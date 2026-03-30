import type { TruthResult } from '../types/verification'

/**
 * Filter phase-level truths to only those whose evidence_files
 * reference the given section ID via "sectie X.Y" or "section X.Y".
 * Truths with empty evidence_files are excluded (phase-level only).
 */
export function filterTruthsForSection(truths: TruthResult[], sectionId: string): TruthResult[] {
  return truths.filter(truth => {
    if (truth.evidence_files.length === 0) return false
    return truth.evidence_files.some(file => {
      const match = file.match(/(?:sectie|section)\s+([\d.]+)/i)
      return match ? match[1] === sectionId : false
    })
  })
}
