import { NavLink } from "react-router-dom"
import { LayoutDashboard, Shield, Activity, Settings, Bell, Database } from "lucide-react"

export function Sidebar() {
  const navItems = [
    { name: "Dashboard", to: "/", icon: <LayoutDashboard className="h-5 w-5" /> },
    { name: "Investigations", to: "/investigations", icon: <Shield className="h-5 w-5" /> },
    { name: "Intelligence", to: "/intelligence", icon: <Database className="h-5 w-5" /> },
    { name: "Alerts", to: "/alerts", icon: <Bell className="h-5 w-5" /> },
    { name: "Analytics", to: "/analytics", icon: <Activity className="h-5 w-5" /> },
    { name: "Settings", to: "/settings", icon: <Settings className="h-5 w-5" /> },
  ]

  return (
    <div className="flex h-full w-64 flex-col bg-sidebar border-r border-border">
      <div className="p-6 flex items-center gap-3">
        <Shield className="h-8 w-8 text-primary" />
        <span className="text-xl font-bold tracking-tight text-slate-900">CounterGuard</span>
      </div>

      <nav className="flex-1 space-y-1 px-3">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-slate-200 text-slate-900"
                  : "text-muted hover:bg-slate-200/50 hover:text-slate-900"
              }`
            }
          >
            {item.icon}
            {item.name}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-border">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-white font-semibold">
            CG
          </div>
          <div className="text-sm">
            <p className="font-medium text-slate-900">Investigator</p>
            <p className="text-xs text-muted">admin@counterguard.ai</p>
          </div>
        </div>
      </div>
    </div>
  )
}
