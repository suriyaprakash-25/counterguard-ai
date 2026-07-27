import { Outlet } from "react-router-dom"
import { Sidebar } from "./Sidebar"
import { TopNavigation } from "./TopNavigation"

export function MainLayout() {
  return (
    <div className="flex h-screen w-full bg-background overflow-hidden text-foreground">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <TopNavigation />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
