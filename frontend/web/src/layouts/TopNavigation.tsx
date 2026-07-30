import { Search, ChevronDown, User, Settings, LogOut, Shield, Moon, Sun } from "lucide-react"
import { NotificationCenter } from "../components/common/NotificationCenter"
import { useAuth } from "../features/auth/useAuth"
import { useState, useRef, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useDarkMode } from "../context/DarkModeContext"
import { CommandPalette } from "../components/common/CommandPalette"

export function TopNavigation() {
  const { user, logout } = useAuth()
  const { darkMode, toggleDarkMode } = useDarkMode()
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isCmdPaletteOpen, setIsCmdPaletteOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const handleLogout = async () => {
    setIsMenuOpen(false)
    await logout()
    navigate('/login')
  }

  return (
    <>
      <CommandPalette isOpen={isCmdPaletteOpen} onClose={() => setIsCmdPaletteOpen(false)} />
      <header className="h-16 border-b border-border bg-surface flex items-center justify-between px-6">
        <div className="flex items-center flex-1">
          <div
            onClick={() => setIsCmdPaletteOpen(true)}
            className="relative w-96 cursor-pointer"
          >
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted" />
            <input
              type="text"
              readOnly
              placeholder="Search products, sellers, or commands (Ctrl+K)..."
              className="h-9 w-full rounded-md border border-border bg-background pl-9 pr-12 text-sm outline-none cursor-pointer focus:border-primary focus:ring-1 focus:ring-primary transition-shadow"
            />
            <span className="absolute right-2.5 top-2 px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-700 text-[10px] font-mono text-slate-600 dark:text-slate-300">
              ⌘K
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Dark Mode Toggle */}
          <button
            onClick={toggleDarkMode}
            className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title={darkMode ? "Switch to Light Mode" : "Switch to SOC Dark Mode"}
          >
            {darkMode ? <Sun className="h-5 w-5 text-amber-400" /> : <Moon className="h-5 w-5 text-slate-600" />}
          </button>

          <NotificationCenter />

          {/* User Profile Menu */}
          <div className="relative" ref={menuRef}>
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="flex items-center gap-3 hover:bg-slate-50 p-1.5 rounded-lg transition-colors focus:outline-none"
            >
              <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold border border-blue-200">
                {user?.firstName?.[0] || 'U'}{user?.lastName?.[0] || ''}
              </div>
              <div className="flex flex-col items-start hidden md:flex">
                <span className="text-sm font-semibold text-slate-700 leading-tight">
                  {user?.firstName} {user?.lastName}
                </span>
                <span className="text-xs font-medium text-slate-500 leading-tight">
                  {user?.role} • {user?.organization}
                </span>
              </div>
              <ChevronDown className={`h-4 w-4 text-slate-400 transition-transform ${isMenuOpen ? 'rotate-180' : ''}`} />
            </button>

            {isMenuOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-slate-100 overflow-hidden z-50">
                <div className="p-3 border-b border-slate-100">
                  <p className="text-sm font-semibold text-slate-800">{user?.email}</p>
                  <div className="flex items-center gap-1 mt-1 text-xs text-slate-500 font-medium">
                    <Shield className="h-3 w-3" />
                    Access Level: {user?.role}
                  </div>
                </div>
                <div className="p-1">
                  <button className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 rounded-lg transition-colors">
                    <User className="h-4 w-4" /> My Profile
                  </button>
                  <button
                    onClick={() => { setIsMenuOpen(false); navigate('/settings'); }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 rounded-lg transition-colors"
                  >
                    <Settings className="h-4 w-4" /> Settings
                  </button>
                </div>
                <div className="p-1 border-t border-slate-100">
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors font-medium"
                  >
                    <LogOut className="h-4 w-4" /> Sign Out
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>
    </>
  )
}
