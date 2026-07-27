import { Search } from "lucide-react"
import { NotificationCenter } from "../components/common/NotificationCenter"

export function TopNavigation() {
  return (
    <header className="h-16 border-b border-border bg-surface flex items-center justify-between px-6">
      <div className="flex items-center flex-1">
        <div className="relative w-96">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted" />
          <input
            type="text"
            placeholder="Search investigations, sellers, or entities..."
            className="h-9 w-full rounded-md border border-border bg-background pl-9 pr-4 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <NotificationCenter />
      </div>
    </header>
  )
}
