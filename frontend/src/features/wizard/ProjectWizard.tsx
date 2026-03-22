import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { AnimatePresence, motion } from 'motion/react'
import { ArrowLeft, ArrowRight, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import { StepIndicator } from './components/StepIndicator'
import { Step1NameDescription } from './components/Step1NameDescription'
import { Step2TypeClassification } from './components/Step2TypeClassification'
import { Step3LanguageConfirm } from './components/Step3LanguageConfirm'
import { Step4DocTypeChecklist } from './components/Step4DocTypeChecklist'
import type { DocTypeFileEntry } from './components/Step4DocTypeChecklist'
import { useCreateProject } from '@/features/projects/queries'
import { useFileUpload } from '@/features/files/hooks/useFileUpload'
import type { WizardFormData, WizardStep } from './types'

const slideVariants = {
  enter: (direction: number) => ({
    x: direction > 0 ? 300 : -300,
    opacity: 0,
  }),
  center: {
    x: 0,
    opacity: 1,
  },
  exit: (direction: number) => ({
    x: direction < 0 ? 300 : -300,
    opacity: 0,
  }),
}

export function ProjectWizard() {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState<WizardStep>(1)
  const [direction, setDirection] = useState(0)
  const [selectedFiles, setSelectedFiles] = useState<DocTypeFileEntry[]>([])
  const [skippedDocTypes, setSkippedDocTypes] = useState<string[]>([])

  const {
    register,
    control,
    handleSubmit,
    watch,
    trigger,
    formState: { errors },
  } = useForm<WizardFormData>({
    mode: 'onChange',
    defaultValues: {
      name: '',
      description: '',
      type: undefined,
      language: undefined,
    },
  })

  const createProjectMutation = useCreateProject()
  const [createdProjectId, setCreatedProjectId] = useState<number | null>(null)

  // File upload hook (only active after project creation)
  const { uploadFile, progressMap, isUploading } = useFileUpload({
    projectId: createdProjectId || undefined,
    onUploadComplete: () => {
      if (createdProjectId) {
        navigate(`/projects/${createdProjectId}`)
      }
    },
  })

  const formData = watch()

  const canProceedStep1 = !!formData.name && formData.name.length > 0
  const canProceedStep2 = !!formData.type
  const canProceedStep3 = !!formData.language
  const canProceedStep4 = true // Files are optional

  const handleNext = async () => {
    let isStepValid = false

    if (currentStep === 1) {
      isStepValid = await trigger(['name'])
      if (isStepValid && canProceedStep1) {
        setDirection(1)
        setCurrentStep(2)
      }
    } else if (currentStep === 2) {
      isStepValid = await trigger(['type'])
      if (isStepValid && canProceedStep2) {
        setDirection(1)
        setCurrentStep(3)
      }
    } else if (currentStep === 3) {
      isStepValid = await trigger(['language'])
      if (isStepValid && canProceedStep3) {
        setDirection(1)
        setCurrentStep(4)
      }
    }
  }

  const handleBack = () => {
    if (currentStep > 1) {
      setDirection(-1)
      setCurrentStep((prev) => (prev - 1) as WizardStep)
    }
  }

  const handleFilesChanged = (entries: DocTypeFileEntry[]) => {
    setSelectedFiles(entries)
  }

  const handleSkippedChanged = (skipped: string[]) => {
    setSkippedDocTypes(skipped)
  }

  const onSubmit = async (data: WizardFormData) => {
    try {
      const newProject = await createProjectMutation.mutateAsync({
        name: data.name,
        type: data.type,
        language: data.language,
      })
      setCreatedProjectId(newProject.id)

      // Persist skipped doc types if any
      if (skippedDocTypes.length > 0) {
        await fetch(`/api/projects/${newProject.id}/skipped-doc-types`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ skipped: skippedDocTypes }),
        })
      }

      // Upload files if any were selected, each with its doc_type
      if (selectedFiles.length > 0) {
        for (const entry of selectedFiles) {
          try {
            await uploadFile(entry.file, undefined, entry.docType)
          } catch (error) {
            console.error(`Failed to upload ${entry.file.name}:`, error)
          }
        }
        navigate(`/projects/${newProject.id}`)
      } else {
        navigate(`/projects/${newProject.id}`)
      }
    } catch (error) {
      console.error('Failed to create project:', error)
    }
  }

  const handleSkipAndCreate = async () => {
    // Create project without files
    const data = formData as WizardFormData
    try {
      const newProject = await createProjectMutation.mutateAsync({
        name: data.name,
        type: data.type,
        language: data.language,
      })
      navigate(`/projects/${newProject.id}`)
    } catch (error) {
      console.error('Failed to create project:', error)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container py-8">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate('/')}
            className="mb-4"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Terug naar overzicht
          </Button>
          <h1 className="text-4xl font-bold tracking-tight">Nieuw project aanmaken</h1>
          <p className="text-muted-foreground mt-1">
            Volg de onderstaande stappen om uw FDS documentatieproject in te richten
          </p>
        </div>

        {/* Wizard Card */}
        <Card className="max-w-2xl mx-auto p-8">
          <form onSubmit={handleSubmit(onSubmit)}>
            {/* Step Indicator */}
            <div className="mb-8">
              <StepIndicator currentStep={currentStep} />
            </div>

            {/* Step Content */}
            <div className="min-h-[400px] mb-8">
              <AnimatePresence mode="wait" custom={direction}>
                {currentStep === 1 && (
                  <motion.div
                    key="step1"
                    custom={direction}
                    variants={slideVariants}
                    initial="enter"
                    animate="center"
                    exit="exit"
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  >
                    <Step1NameDescription register={register} errors={errors} />
                  </motion.div>
                )}

                {currentStep === 2 && (
                  <motion.div
                    key="step2"
                    custom={direction}
                    variants={slideVariants}
                    initial="enter"
                    animate="center"
                    exit="exit"
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  >
                    <Step2TypeClassification control={control} errors={errors} />
                  </motion.div>
                )}

                {currentStep === 3 && (
                  <motion.div
                    key="step3"
                    custom={direction}
                    variants={slideVariants}
                    initial="enter"
                    animate="center"
                    exit="exit"
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  >
                    <Step3LanguageConfirm control={control} watch={watch} />
                  </motion.div>
                )}

                {currentStep === 4 && (
                  <motion.div
                    key="step4"
                    custom={direction}
                    variants={slideVariants}
                    initial="enter"
                    animate="center"
                    exit="exit"
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  >
                    <Step4DocTypeChecklist
                      projectType={formData.type || 'A'}
                      onFilesChanged={handleFilesChanged}
                      onSkippedChanged={handleSkippedChanged}
                      progressMap={progressMap}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Error Display */}
            {createProjectMutation.isError && (
              <div className="mb-6">
                <ErrorMessage
                  title="Project aanmaken mislukt"
                  message={
                    createProjectMutation.error instanceof Error
                      ? createProjectMutation.error.message
                      : 'An unexpected error occurred'
                  }
                  onRetry={() => createProjectMutation.reset()}
                />
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex items-center justify-between pt-6 border-t">
              <div>
                {currentStep > 1 && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleBack}
                    disabled={createProjectMutation.isPending}
                  >
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    Vorige
                  </Button>
                )}
              </div>

              <div className="flex gap-2">
                {currentStep < 4 ? (
                  <Button
                    type="button"
                    onClick={handleNext}
                    disabled={
                      (currentStep === 1 && !canProceedStep1) ||
                      (currentStep === 2 && !canProceedStep2) ||
                      (currentStep === 3 && !canProceedStep3)
                    }
                  >
                    Volgende
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                ) : (
                  <>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={handleSkipAndCreate}
                      disabled={createProjectMutation.isPending || isUploading}
                    >
                      Overslaan & aanmaken
                    </Button>
                    <Button
                      type="submit"
                      disabled={
                        !canProceedStep4 || createProjectMutation.isPending || isUploading
                      }
                    >
                      {createProjectMutation.isPending || isUploading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          {createProjectMutation.isPending ? 'Aanmaken...' : 'Uploaden...'}
                        </>
                      ) : (
                        'Project aanmaken'
                      )}
                    </Button>
                  </>
                )}
              </div>
            </div>
          </form>
        </Card>
      </div>
    </div>
  )
}
