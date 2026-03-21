import { createContext, useContext, useReducer, useEffect, useCallback, useMemo } from 'react'
import type { ReactNode } from 'react'
import type { SectionReview, ReviewContextValue } from '../types/verification'

const STORAGE_KEY = (projectId: number, phaseNumber: number) =>
  `review-session-${projectId}-${phaseNumber}`

type ReviewAction =
  | { type: 'SET_REVIEW'; sectionId: string; status: SectionReview['status']; feedback: string }
  | { type: 'CLEAR' }
  | { type: 'LOAD'; reviews: Record<string, SectionReview> }

function reviewReducer(
  state: Record<string, SectionReview>,
  action: ReviewAction
): Record<string, SectionReview> {
  switch (action.type) {
    case 'SET_REVIEW':
      return {
        ...state,
        [action.sectionId]: {
          sectionId: action.sectionId,
          status: action.status,
          feedback: action.feedback,
          timestamp: Date.now(),
        },
      }
    case 'CLEAR':
      return {}
    case 'LOAD':
      return action.reviews
    default:
      return state
  }
}

const ReviewContext = createContext<ReviewContextValue | null>(null)

interface ReviewProviderProps {
  projectId: number
  phaseNumber: number
  children: ReactNode
}

export function ReviewProvider({ projectId, phaseNumber, children }: ReviewProviderProps) {
  const storageKey = STORAGE_KEY(projectId, phaseNumber)

  const [reviews, dispatch] = useReducer(reviewReducer, {}, () => {
    try {
      const stored = localStorage.getItem(storageKey)
      return stored ? JSON.parse(stored) : {}
    } catch {
      return {}
    }
  })

  // Persist on change
  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(reviews))
  }, [reviews, storageKey])

  const setReview = useCallback(
    (sectionId: string, status: SectionReview['status'], feedback: string) => {
      dispatch({ type: 'SET_REVIEW', sectionId, status, feedback })
    },
    []
  )

  const clearReviews = useCallback(() => {
    dispatch({ type: 'CLEAR' })
  }, [])

  const exportAsJson = useCallback(() => {
    return JSON.stringify(
      {
        phaseNumber,
        exportedAt: new Date().toISOString(),
        sections: Object.values(reviews).map((r) => ({
          section_id: r.sectionId,
          status: r.status === 'goedgekeurd' ? 'Approved' : r.status === 'opmerking' ? 'Comment' : 'Flag',
          finding: r.feedback || '-',
        })),
      },
      null,
      2
    )
  }, [phaseNumber, reviews])

  const reviewedCount = useMemo(() => Object.keys(reviews).length, [reviews])

  const value = useMemo<ReviewContextValue>(
    () => ({ reviews, setReview, clearReviews, exportAsJson, reviewedCount }),
    [reviews, setReview, clearReviews, exportAsJson, reviewedCount]
  )

  return <ReviewContext.Provider value={value}>{children}</ReviewContext.Provider>
}

export function useReviewContext(): ReviewContextValue | null {
  return useContext(ReviewContext)
}
