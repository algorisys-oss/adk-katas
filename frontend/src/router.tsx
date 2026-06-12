import { createBrowserRouter } from "react-router-dom"
import { Layout } from "@/components/Layout"
import { HomePage } from "@/pages/HomePage"
import { KataPage } from "@/pages/KataPage"

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "kata/:slug", element: <KataPage /> },
    ],
  },
])
