import type { SectionReview } from '../types/verification'

export function readReviewSession(
  projectId: number,
  phaseNumber: number
): Record<string, SectionReview> {
  try {
    const key = `review-session-${projectId}-${phaseNumber}`
    const stored = localStorage.getItem(key)
    return stored ? JSON.parse(stored) : {}
  } catch {
    return {}
  }
}

export function countRejected(reviews: Record<string, SectionReview>): number {
  return Object.values(reviews).filter(r => r.status === 'afgewezen').length
}

export function countAllRejected(projectId: number): number {
  let total = 0
  for (const key of Object.keys(localStorage)) {
    if (key.startsWith(`review-session-${projectId}-`)) {
      try {
        const reviews: Record<string, SectionReview> = JSON.parse(localStorage.getItem(key) || '{}')
        total += countRejected(reviews)
      } catch {
        // skip malformed entries
      }
    }
  }
  return total
}
