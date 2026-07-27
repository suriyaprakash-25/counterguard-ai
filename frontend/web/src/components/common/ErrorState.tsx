import { AlertTriangle } from "lucide-react"
import { Button } from "./Button"

interface ErrorStateProps {
  title?: string
  message: string
  onRetry?: () => void
}

export function ErrorState({ title = "Something went wrong", message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center rounded-xl bg-red-50 border border-red-100">
      <AlertTriangle className="h-8 w-8 text-red-500 mb-3" />
      <h3 className="text-lg font-semibold text-red-900">{title}</h3>
      <p className="text-sm text-red-700 mt-1 mb-4">{message}</p>
      {onRetry && (
        <Button variant="danger" size="sm" onClick={onRetry}>
          Try Again
        </Button>
      )}
    </div>
  )
}
