import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const navLinks = [
  { to: '/discovery', label: 'Discovery' },
  { to: '/matches', label: 'Matches' },
  { to: '/profile', label: 'Profile' },
  { to: '/stats', label: 'Stats' },
]

export default function Layout() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-6">
        <span className="font-bold text-rose-500 text-lg mr-4">Finder</span>
        {navLinks.map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `text-sm font-medium transition-colors ${
                isActive ? 'text-rose-500' : 'text-gray-600 hover:text-gray-900'
              }`
            }
          >
            {label}
          </NavLink>
        ))}
        <button
          onClick={handleLogout}
          className="ml-auto text-sm text-gray-500 hover:text-gray-900 transition-colors"
        >
          Logout
        </button>
      </nav>
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  )
}
