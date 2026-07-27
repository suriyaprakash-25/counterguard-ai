import { RouterProvider } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { router } from "./routes"
import { GlobalErrorBoundary } from "./components/common/GlobalErrorBoundary"
import { AppProvider } from "./context/AppContext"

const queryClient = new QueryClient()

function App() {
  return (
    <GlobalErrorBoundary>
      <AppProvider>
        <QueryClientProvider client={queryClient}>
          <RouterProvider router={router} />
        </QueryClientProvider>
      </AppProvider>
    </GlobalErrorBoundary>
  )
}

export default App
