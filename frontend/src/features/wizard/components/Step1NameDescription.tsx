import { useEffect } from 'react'
import type { UseFormRegister, FieldErrors } from 'react-hook-form'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import type { WizardFormData } from '../types'

interface Step1NameDescriptionProps {
  register: UseFormRegister<WizardFormData>
  errors: FieldErrors<WizardFormData>
}

export function Step1NameDescription({ register, errors }: Step1NameDescriptionProps) {
  useEffect(() => {
    // Auto-focus name input on mount
    document.getElementById('project-name')?.focus()
  }, [])

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="project-name" className="text-base">
          Projectnaam <span className="text-destructive">*</span>
        </Label>
        <Input
          id="project-name"
          placeholder="bijv. Zuivel Verpakkingslijn"
          {...register('name', {
            required: 'Projectnaam is verplicht',
            minLength: { value: 1, message: 'Projectnaam moet minimaal 1 teken bevatten' },
            maxLength: { value: 255, message: 'Projectnaam mag maximaal 255 tekens bevatten' },
          })}
          className={errors.name ? 'border-destructive' : ''}
        />
        {errors.name && (
          <p className="text-sm text-destructive">{errors.name.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="project-description" className="text-base">
          Beschrijving (optioneel)
        </Label>
        <Textarea
          id="project-description"
          placeholder="Korte beschrijving van de projectscope en doelstellingen..."
          rows={4}
          {...register('description')}
        />
        <p className="text-sm text-muted-foreground">
          Geef indien nodig extra context over het project
        </p>
      </div>
    </div>
  )
}
