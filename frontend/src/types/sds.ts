/**
 * TypeScript types for SDS scaffolding API.
 * Mirrors backend/app/schemas/sds.py exactly.
 */

export type ConfidenceLevel = 'HIGH' | 'MEDIUM' | 'LOW' | 'UNMATCHED'
export type MatchStatus = 'matched' | 'low_confidence' | 'new_typical_needed'

export interface MatchDetail {
  reason: string
  io_score: number
  keyword_score: number
  state_score: number
  category_score: number
  closest_match: string | null
  closest_confidence: number | null
  cli_hint: string
}

export interface TypicalMatch {
  equipment_module: string
  matched_typical: string | null
  typical_id: string | null
  confidence: number
  confidence_level: ConfidenceLevel
  status: MatchStatus
  match_detail: MatchDetail | null
}

export interface SdsResults {
  project_id: number
  scaffold_date: string | null
  total_modules: number
  matched_count: number
  low_confidence_count: number
  unmatched_count: number
  matches: TypicalMatch[]
  catalog_found: boolean
}
