import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

interface ExportOptionsProps {
  mode: string
  language: string
  onModeChange: (mode: string) => void
  onLanguageChange: (lang: string) => void
  disabled: boolean
}

export function ExportOptions({
  mode,
  language,
  onModeChange,
  onLanguageChange,
  disabled,
}: ExportOptionsProps) {
  return (
    <div className="flex flex-row gap-4 items-end">
      <div className="flex flex-col gap-1.5">
        <label className="text-sm font-medium">Exportmodus</label>
        <Select value={mode} onValueChange={onModeChange} disabled={disabled}>
          <SelectTrigger className="w-52">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="draft">Concept (met watermerk)</SelectItem>
            <SelectItem value="final">Definitief</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="flex flex-col gap-1.5">
        <label className="text-sm font-medium">Taal</label>
        <Select value={language} onValueChange={onLanguageChange} disabled={disabled}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="nl">Nederlands</SelectItem>
            <SelectItem value="en">English</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  )
}
