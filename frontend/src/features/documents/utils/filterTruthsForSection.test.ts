import { describe, it, expect } from 'vitest'
import { filterTruthsForSection } from './filterTruthsForSection'
import type { TruthResult } from '../types/verification'

function makeTruth(overrides: Partial<TruthResult> = {}): TruthResult {
  return {
    description: 'Test truth',
    status: 'PASS',
    levels: {
      exists: 'pass',
      substantive: 'pass',
      complete: 'pass',
      consistent: 'pass',
      standards: 'pass',
    },
    failed_level: null,
    gap_description: null,
    evidence_files: [],
    standards_violations: [],
    ...overrides,
  }
}

describe('filterTruthsForSection', () => {
  it('returns truths matching Dutch sectie format', () => {
    const truth = makeTruth({ evidence_files: ['02-01-CONTENT.md, sectie 2.3, regel 45-78'] })
    expect(filterTruthsForSection([truth], '2.3')).toEqual([truth])
  })

  it('returns truths matching English section format', () => {
    const truth = makeTruth({ evidence_files: ['02-01-CONTENT.md, section 2.3, line 45-78'] })
    expect(filterTruthsForSection([truth], '2.3')).toEqual([truth])
  })

  it('exact match prevents 2.1 matching 2.10', () => {
    const truth = makeTruth({ evidence_files: ['02-01-CONTENT.md, sectie 2.10, regel 1-10'] })
    expect(filterTruthsForSection([truth], '2.1')).toEqual([])
  })

  it('exact match prevents 2.1 matching 2.11', () => {
    const truth = makeTruth({ evidence_files: ['02-01-CONTENT.md, sectie 2.11, regel 1-10'] })
    expect(filterTruthsForSection([truth], '2.1')).toEqual([])
  })

  it('excludes truths with empty evidence_files', () => {
    const truth = makeTruth({ evidence_files: [] })
    expect(filterTruthsForSection([truth], '2.3')).toEqual([])
  })

  it('excludes truths with no sectie/section pattern', () => {
    const truth = makeTruth({ evidence_files: ['some-file.md, regel 10'] })
    expect(filterTruthsForSection([truth], '2.3')).toEqual([])
  })

  it('returns empty array for empty truths input', () => {
    expect(filterTruthsForSection([], '2.3')).toEqual([])
  })

  it('matches if ANY evidence file references section', () => {
    const truth = makeTruth({
      evidence_files: ['other.md, sectie 3.1', 'content.md, sectie 2.3, regel 5'],
    })
    expect(filterTruthsForSection([truth], '2.3')).toEqual([truth])
  })

  it('filters mixed truths correctly', () => {
    const matchingTruth = makeTruth({ evidence_files: ['content.md, sectie 2.3, regel 10'] })
    const otherTruth = makeTruth({ evidence_files: ['content.md, sectie 2.4, regel 20'] })
    const emptyTruth = makeTruth({ evidence_files: [] })
    expect(filterTruthsForSection([matchingTruth, otherTruth, emptyTruth], '2.3')).toEqual([matchingTruth])
  })
})
