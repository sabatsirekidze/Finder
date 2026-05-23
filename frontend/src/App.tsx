import { createBrowserRouter, Navigate, RouterProvider } from 'react-router-dom'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DiscoveryPage from './pages/DiscoveryPage'
import MatchesPage from './pages/MatchesPage'
import ChatPage from './pages/ChatPage'
import ProfilePage from './pages/ProfilePage'
import StatsPage from './pages/StatsPage'

const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <Layout />,
        children: [
          { path: '/', element: <Navigate to="/discovery" replace /> },
          { path: '/discovery', element: <DiscoveryPage /> },
          { path: '/matches', element: <MatchesPage /> },
          { path: '/matches/:id', element: <ChatPage /> },
          { path: '/profile', element: <ProfilePage /> },
          { path: '/stats', element: <StatsPage /> },
        ],
      },
    ],
  },
])

export default function App() {
  return <RouterProvider router={router} />
}
