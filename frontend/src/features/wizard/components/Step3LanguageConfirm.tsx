import { Controller } from 'react-hook-form'
import type { Control, UseFormWatch } from 'react-hook-form'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { motion } from 'motion/react'
import type { WizardFormData } from '../types'

interface Step3LanguageConfirmProps {
  control: Control<WizardFormData>
  watch: UseFormWatch<WizardFormData>
}

const languages = [
  { id: 'nl' as const, label: 'Nederlands', badge: 'NL', flag: '🇳🇱' },
  { id: 'en' as const, label: 'Engels', badge: 'EN', flag: '🇬🇧' },
]

const projectTypeLabels = {
  A: 'Nieuwbouw + Standaarden',
  B: 'Nieuwbouw Flex',
  C: 'Modificatie Groot',
  D: 'Modificatie Klein / TWN',
}

export function Step3LanguageConfirm({ control, watch }: Step3LanguageConfirmProps) {
  const formData = watch()

  return (
    <div className="space-y-8">
      {/* Language Selection */}
      <div className="space-y-4">
        <div className="space-y-2">
          <h2 className="text-lg font-semibold">
            Selecteer taal <span className="text-destructive">*</span>
          </h2>
          <p className="text-sm text-muted-foreground">
            Kies de primaire taal voor uw FDS documentatie
          </p>
        </div>

        <Controller
          name="language"
          control={control}
          rules={{ required: 'Selecteer een taal' }}
          render={({ field }) => (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {languages.map((lang) => (
                <motion.button
                  key={lang.id}
                  type="button"
                  onClick={() => field.onChange(lang.id)}
                  className={`
                    p-6 rounded-lg border-2 transition-all text-left
                    ${
                      field.value === lang.id
                        ? 'ring-2 ring-primary bg-primary/5 border-primary'
                        : 'border-border bg-card hover:shadow-md'
                    }
                  `}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{lang.flag}</span>
                    <div>
                      <p className="font-semibold text-lg">{lang.label}</p>
                      <Badge variant="outline" className="mt-1">
                        {lang.badge}
                      </Badge>
                    </div>
                  </div>
                </motion.button>
              ))}
            </div>
          )}
        />
      </div>

      {/* Confirmation Summary */}
      <Card className="p-6 bg-muted/50">
        <h3 className="font-semibold text-lg mb-4">Samenvatting</h3>
        <div className="space-y-3">
          <div>
            <p className="text-sm text-muted-foreground">Projectnaam</p>
            <p className="font-medium">{formData.name || '—'}</p>
          </div>
          {formData.description && (
            <div>
              <p className="text-sm text-muted-foreground">Beschrijving</p>
              <p className="text-sm">{formData.description}</p>
            </div>
          )}
          <div>
            <p className="text-sm text-muted-foreground">Type</p>
            <div className="flex items-center gap-2 mt-1">
              <Badge
                variant="outline"
                className={`
                  ${formData.type === 'A' && 'border-blue-500 text-blue-500'}
                  ${formData.type === 'B' && 'border-emerald-500 text-emerald-500'}
                  ${formData.type === 'C' && 'border-amber-500 text-amber-500'}
                  ${formData.type === 'D' && 'border-rose-500 text-rose-500'}
                `}
              >
                Type {formData.type}
              </Badge>
              <p className="text-sm">
                {formData.type ? projectTypeLabels[formData.type] : '—'}
              </p>
            </div>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Taal</p>
            <p className="font-medium">
              {formData.language === 'nl' ? 'Nederlands (NL)' : formData.language === 'en' ? 'Engels (EN)' : '—'}
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}
