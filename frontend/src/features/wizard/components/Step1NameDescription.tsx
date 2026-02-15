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
          Project Name <span className="text-destructive">*</span>
        </Label>
        <Input
          id="project-name"
          placeholder="e.g., Dairy Packaging Line"
          {...register('name', {
            required: 'Project name is required',
            minLength: { value: 1, message: 'Project name must be at least 1 character' },
            maxLength: { value: 255, message: 'Project name must not exceed 255 characters' },
          })}
          className={errors.name ? 'border-destructive' : ''}
        />
        {errors.name && (
          <p className="text-sm text-destructive">{errors.name.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="project-description" className="text-base">
          Description (Optional)
        </Label>
        <Textarea
          id="project-description"
          placeholder="Brief description of the project scope and objectives..."
          rows={4}
          {...register('description')}
        />
        <p className="text-sm text-muted-foreground">
          Provide additional context about the project if needed
        </p>
      </div>
    </div>
  )
}
