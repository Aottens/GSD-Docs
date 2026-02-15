import { Check } from 'lucide-react'
import { motion } from 'motion/react'
import type { WizardStep } from '../types'

interface StepIndicatorProps {
  currentStep: WizardStep
}

const steps = [
  { step: 1, label: 'Projectinfo' },
  { step: 2, label: 'Type' },
  { step: 3, label: 'Taal' },
  { step: 4, label: 'Referenties' },
]

export function StepIndicator({ currentStep }: StepIndicatorProps) {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => (
          <div key={step.step} className="flex items-center flex-1">
            {/* Step circle */}
            <div className="relative flex flex-col items-center">
              <motion.div
                className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors ${
                  currentStep > step.step
                    ? 'border-primary bg-primary text-primary-foreground'
                    : currentStep === step.step
                      ? 'border-primary bg-background text-primary'
                      : 'border-muted bg-background text-muted-foreground'
                }`}
                initial={false}
                animate={{
                  scale: currentStep === step.step ? 1.1 : 1,
                }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              >
                {currentStep > step.step ? (
                  <Check className="w-5 h-5" />
                ) : (
                  <span className="font-semibold">{step.step}</span>
                )}
              </motion.div>
              <p
                className={`mt-2 text-sm font-medium ${
                  currentStep >= step.step ? 'text-foreground' : 'text-muted-foreground'
                }`}
              >
                {step.label}
              </p>
            </div>

            {/* Connector line */}
            {index < steps.length - 1 && (
              <div className="flex-1 mx-4 h-[2px] bg-border relative">
                <motion.div
                  className="absolute inset-0 bg-primary"
                  initial={{ scaleX: 0 }}
                  animate={{ scaleX: currentStep > step.step ? 1 : 0 }}
                  transition={{ type: 'spring', stiffness: 200, damping: 25 }}
                  style={{ transformOrigin: 'left' }}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
