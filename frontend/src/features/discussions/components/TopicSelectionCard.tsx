import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { HelpCircle } from 'lucide-react'

interface Topic {
  name: string
  description: string
}

interface TopicSelectionCardProps {
  topics: Topic[]
  onConfirm: (selectedTopics: string[], discretionTopics: string[]) => void
}

export function TopicSelectionCard({ topics, onConfirm }: TopicSelectionCardProps) {
  const [selectedTopics, setSelectedTopics] = useState<Set<string>>(new Set())
  const [discretionEnabled, setDiscretionEnabled] = useState(false)

  const handleTopicToggle = (topicName: string) => {
    const newSelected = new Set(selectedTopics)
    if (newSelected.has(topicName)) {
      newSelected.delete(topicName)
    } else {
      newSelected.add(topicName)
    }
    setSelectedTopics(newSelected)
  }

  const handleConfirm = () => {
    const selected = Array.from(selectedTopics)
    const discretion = discretionEnabled
      ? topics.filter((t) => !selectedTopics.has(t.name)).map((t) => t.name)
      : []
    onConfirm(selected, discretion)
  }

  return (
    <Card className="p-6 space-y-4 max-w-2xl">
      <h3 className="text-lg font-semibold">Onderwerpen voor bespreking</h3>
      <p className="text-sm text-muted-foreground">
        Selecteer de onderwerpen die u wilt bespreken. Niet-geselecteerde onderwerpen worden
        overgeslagen.
      </p>

      <div className="space-y-3">
        {topics.map((topic, idx) => (
          <div key={idx} className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted/50">
            <Checkbox
              id={`topic-${idx}`}
              checked={selectedTopics.has(topic.name)}
              onCheckedChange={() => handleTopicToggle(topic.name)}
            />
            <div className="flex-1">
              <Label htmlFor={`topic-${idx}`} className="font-medium cursor-pointer">
                {topic.name}
              </Label>
              <p className="text-sm text-muted-foreground">{topic.description}</p>
            </div>
          </div>
        ))}

        {/* Discretion option */}
        <div className="flex items-start gap-3 p-3 rounded-lg border-2 border-dashed hover:bg-muted/50">
          <Checkbox
            id="discretion"
            checked={discretionEnabled}
            onCheckedChange={(checked: boolean) => setDiscretionEnabled(checked as boolean)}
          />
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <Label htmlFor="discretion" className="font-medium cursor-pointer">
                Overige als Claude's Discretie
              </Label>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <HelpCircle className="h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent className="max-w-xs">
                    <p>
                      Claude bepaalt zelf of niet-geselecteerde onderwerpen besproken moeten worden
                      op basis van projectcontext. Bespaart tijd bij standaard onderwerpen.
                    </p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
            <p className="text-sm text-muted-foreground">
              Laat Claude beslissen over de overige onderwerpen
            </p>
          </div>
        </div>
      </div>

      <Button
        onClick={handleConfirm}
        disabled={selectedTopics.size === 0 && !discretionEnabled}
        className="w-full"
      >
        Bevestig selectie
      </Button>
    </Card>
  )
}
