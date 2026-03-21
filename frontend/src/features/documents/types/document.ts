/**
 * TypeScript interfaces for document outline and section content.
 * These mirror the backend Pydantic schemas exactly (app/schemas/document.py).
 */

export interface PlanInfo {
  wave: number
  depends_on: string[]
  plan_name: string
  plan_file: string
  truths: string[]               // must-have truths from PLAN.md frontmatter must_haves.truths
  description: string | null     // plan description from PLAN.md <objective> block
}

export interface OutlineNode {
  id: string                    // "1", "1.1", "4.2.3"
  title: { en: string; nl: string }
  depth: number                 // 1, 2, 3
  required: boolean
  source_type: string           // "system-overview", "dynamic", "auto-generated", "placeholder"
  status: 'empty' | 'planned' | 'written' | 'verified'
  has_content: boolean
  has_plan: boolean
  plan_info: PlanInfo | null
  preview_snippet: string | null
  children: OutlineNode[]
}

export interface DocumentOutlineResponse {
  project_id: number
  project_language: 'nl' | 'en'
  sections: OutlineNode[]
}

export interface SectionContentResponse {
  section_id: string
  status: 'empty' | 'planned' | 'written' | 'verified'
  markdown_content: string | null
  plan_info: PlanInfo | null
}
