import { Controller } from 'react-hook-form'
import type { Control, FieldErrors } from 'react-hook-form'
import { TypeCard } from './TypeCard'
import type { WizardFormData, TypeInfo } from '../types'

interface Step2TypeClassificationProps {
  control: Control<WizardFormData>
  errors: FieldErrors<WizardFormData>
}

const projectTypes: TypeInfo[] = [
  {
    id: 'A',
    title: 'New Installation',
    description: 'Complete FDS for a new production line or system',
    example: 'New packaging line for dairy products',
    icon: 'plus-circle',
  },
  {
    id: 'B',
    title: 'Standard System',
    description: 'FDS based on a standardized system design with minor customization',
    example: 'Standard CIP system with site-specific I/O',
    icon: 'layers',
  },
  {
    id: 'C',
    title: 'Modification',
    description: 'FDS for modifying an existing installation',
    example: 'Adding a new dosing unit to existing batch system',
    icon: 'wrench',
  },
  {
    id: 'D',
    title: 'Migration',
    description: 'FDS for control system migration (hardware/software)',
    example: 'PLC migration from S7-300 to S7-1500',
    icon: 'arrow-right-left',
  },
]

export function Step2TypeClassification({ control, errors }: Step2TypeClassificationProps) {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h2 className="text-lg font-semibold">
          Select Project Type <span className="text-destructive">*</span>
        </h2>
        <p className="text-sm text-muted-foreground">
          Choose the category that best describes your FDS project
        </p>
      </div>

      <Controller
        name="type"
        control={control}
        rules={{ required: 'Please select a project type' }}
        render={({ field }) => (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {projectTypes.map((type) => (
              <TypeCard
                key={type.id}
                type={type}
                isSelected={field.value === type.id}
                onClick={() => field.onChange(type.id)}
              />
            ))}
          </div>
        )}
      />

      {errors.type && (
        <p className="text-sm text-destructive">{errors.type.message}</p>
      )}
    </div>
  )
}
