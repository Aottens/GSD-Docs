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
    title: 'Nieuwbouw + Standaarden',
    description: 'New installation with formal standards compliance (PackML, ISA-88). Full FDS structure with enforced standards verification at each phase.',
    example: 'New packaging line with full ISA-88 equipment hierarchy',
    icon: 'plus-circle',
  },
  {
    id: 'B',
    title: 'Nieuwbouw Flex',
    description: 'New installation with flexible standards approach. Pragmatic structure without strict ISA-88/PackML enforcement.',
    example: 'New CIP system with standards applied where beneficial',
    icon: 'layers',
  },
  {
    id: 'C',
    title: 'Modificatie Groot',
    description: 'Large modification to an existing system. Documents only the delta against the baseline — existing system treated as immutable.',
    example: 'Adding a new dosing unit to existing batch system',
    icon: 'wrench',
  },
  {
    id: 'D',
    title: 'Modificatie Klein / TWN',
    description: 'Small modification or Technische Wijzigingsnotitie. Minimal structure documenting the change, implementation, and test criteria.',
    example: 'Replacing mixer motor with updated model in EM-200',
    icon: 'arrow-right-left',
  },
]

export function Step2TypeClassification({ control, errors }: Step2TypeClassificationProps) {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h2 className="text-lg font-semibold">
          Selecteer projecttype <span className="text-destructive">*</span>
        </h2>
        <p className="text-sm text-muted-foreground">
          Kies de categorie die het beste past bij uw FDS project
        </p>
      </div>

      <Controller
        name="type"
        control={control}
        rules={{ required: 'Selecteer een projecttype' }}
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
