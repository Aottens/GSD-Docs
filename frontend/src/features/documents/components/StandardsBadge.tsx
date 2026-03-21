import { Badge } from '@/components/ui/badge'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'

interface StandardsBadgeProps {
  reference: string
  text: string
}

export function StandardsBadge({ reference, text }: StandardsBadgeProps) {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Badge variant="outline" className="text-xs font-normal cursor-default">
            {reference}
          </Badge>
        </TooltipTrigger>
        <TooltipContent className="max-w-xs">
          {text}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}
