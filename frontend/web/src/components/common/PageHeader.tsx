import type { ReactNode } from "react"
import { cn } from "../../utils/cn"

export function PageHeader({ title, description, children, className }: { title: string, description?: string, children?: ReactNode, className?: string }) {
  return (
    <div className={cn("flex items-center justify-between pb-6", className)}>
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">{title}</h1>
        {description && <p className="text-muted mt-1">{description}</p>}
      </div>
      {children && <div className="flex items-center gap-3">{children}</div>}
    </div>
  )
}
