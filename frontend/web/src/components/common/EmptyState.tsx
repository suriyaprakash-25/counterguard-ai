import type { LucideIcon } from "lucide-react"

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  action?: React.ReactNode
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border border-border border-dashed rounded-xl bg-slate-50/50">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 mb-4">
        <Icon className="h-6 w-6 text-muted" />
      </div>
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      <p className="text-sm text-muted mt-1 mb-4 max-w-sm">{description}</p>
      {action}
    </div>
  )
}
