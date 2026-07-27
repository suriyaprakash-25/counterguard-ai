import { RouterProvider } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { router } from "./routes"
import { AppProvider } from "./context/AppContext"

const queryClient = new QueryClient()

function App() {
  return (
    <AppProvider>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </AppProvider>
  )
}

export default App
