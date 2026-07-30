import { createBrowserRouter } from "react-router-dom"
import { lazy, Suspense } from "react"
import { MainLayout } from "../layouts/MainLayout"
import { ProtectedRoute } from "../features/auth/components/ProtectedRoute"
import { LoadingSkeleton } from "../components/common/LoadingSkeleton"

const Dashboard = lazy(() => import("../pages/Dashboard"))
const Investigations = lazy(() => import("../pages/Investigations"))
const InvestigationDetails = lazy(() => import("../pages/InvestigationDetails"))
const Intelligence = lazy(() => import("../pages/Intelligence"))
const ProductIntelligence = lazy(() => import("../pages/ProductIntelligence"))
const Monitoring = lazy(() => import("../pages/Monitoring"))
const GraphExplorer = lazy(() => import("../pages/GraphExplorer"))
const FraudRings = lazy(() => import("../pages/FraudRings"))
const Alerts = lazy(() => import("../pages/Alerts"))
const Analytics = lazy(() => import("../pages/Analytics"))
const Settings = lazy(() => import("../pages/Settings"))
const Login = lazy(() => import("../features/auth/routes/Login"))
const UnauthorizedPage = lazy(() => import("../features/auth/routes/Unauthorized").then(m => ({ default: m.Unauthorized })))

const SuspenseWrapper = ({ children }: { children: React.ReactNode }) => (
  <Suspense fallback={<div className="p-8"><LoadingSkeleton className="h-[600px] w-full" /></div>}>
    {children}
  </Suspense>
)

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <SuspenseWrapper><Login /></SuspenseWrapper>,
  },
  {
    path: "/unauthorized",
    element: <SuspenseWrapper><UnauthorizedPage /></SuspenseWrapper>,
  },
  {
    path: "/",
    element: (
      <ProtectedRoute>
        <MainLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <SuspenseWrapper><Dashboard /></SuspenseWrapper> },
      { path: "dashboard", element: <SuspenseWrapper><Dashboard /></SuspenseWrapper> },
      { path: "investigations", element: <SuspenseWrapper><Investigations /></SuspenseWrapper> },
      { path: "investigations/:id", element: <SuspenseWrapper><InvestigationDetails /></SuspenseWrapper> },
      { path: "intelligence", element: <SuspenseWrapper><Intelligence /></SuspenseWrapper> },
      { path: "product-intelligence", element: <SuspenseWrapper><ProductIntelligence /></SuspenseWrapper> },
      { path: "monitoring", element: <SuspenseWrapper><Monitoring /></SuspenseWrapper> },
      { path: "continuous-monitoring", element: <SuspenseWrapper><Monitoring /></SuspenseWrapper> },
      { path: "graph", element: <SuspenseWrapper><GraphExplorer /></SuspenseWrapper> },
      { path: "fraud-rings", element: <SuspenseWrapper><FraudRings /></SuspenseWrapper> },
      { path: "threat/rings", element: <SuspenseWrapper><FraudRings /></SuspenseWrapper> },
      { path: "alerts", element: <SuspenseWrapper><Alerts /></SuspenseWrapper> },
      { path: "analytics", element: <SuspenseWrapper><Analytics /></SuspenseWrapper> },
      { path: "settings", element: <SuspenseWrapper><Settings /></SuspenseWrapper> },
    ],
  },
])
