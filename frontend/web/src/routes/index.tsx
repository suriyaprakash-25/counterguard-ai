import { createBrowserRouter } from "react-router-dom"
import { MainLayout } from "../layouts/MainLayout"
import Dashboard from "../pages/Dashboard"
import Investigations from "../pages/Investigations"
import InvestigationDetails from "../pages/InvestigationDetails"
import Intelligence from "../pages/Intelligence"
import GraphExplorer from "../pages/GraphExplorer"
import Alerts from "../pages/Alerts"
import Analytics from "../pages/Analytics"
import Settings from "../pages/Settings"

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "dashboard", element: <Dashboard /> },
      { path: "investigations", element: <Investigations /> },
      { path: "investigations/:id", element: <InvestigationDetails /> },
      { path: "intelligence", element: <Intelligence /> },
      { path: "graph", element: <GraphExplorer /> },
      { path: "alerts", element: <Alerts /> },
      { path: "analytics", element: <Analytics /> },
      { path: "settings", element: <Settings /> },
    ],
  },
])
