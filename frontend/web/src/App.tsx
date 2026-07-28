import { RouterProvider } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { router } from "./routes"
import { GlobalErrorBoundary } from "./components/common/GlobalErrorBoundary"
import { AppProvider } from "./context/AppContext"
import { AuthProvider } from "./features/auth/AuthContext"

const queryClient = new QueryClient()

function App() {
  return (
    <GlobalErrorBoundary>
      <AppProvider>
        <QueryClientProvider client={queryClient}>
          <AuthProvider>
            <RouterProvider router={router} />
          </AuthProvider>
        </QueryClientProvider>
      </AppProvider>
    </GlobalErrorBoundary>
  )
}

export default App
