import type { ProjectType, Language } from '@/types/project'

export type WizardStep = 1 | 2 | 3 | 4

export interface WizardFormData {
  name: string
  description: string
  type: ProjectType
  language: Language
  uploadedFiles?: File[]
}

export interface TypeInfo {
  id: ProjectType
  title: string
  description: string
  example: string
  icon: string
}
