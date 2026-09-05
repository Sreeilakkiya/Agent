import React, { useState } from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'

const Layout = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/leaks', label: 'Revenue Leaks', icon: '⚠️' },
    { path: '/prevention', label: 'Prevention', icon: '🛡️' },
    { path: '/recovery', label: 'Recovery', icon: '💰' },
    { path: '/customers', label: 'Customers', icon: '👥' },
    { path: '/upload', label: 'Data Upload', icon: '📁' },
  ]

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-slate-800 text-white transition-all duration-300`}>
        <div className="p-4 border-b border-slate-700">
          <h1 className={`text-xl font-bold ${!sidebarOpen && 'hidden'}`}>FlowRecover</h1>
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-2xl">
            {sidebarOpen ? '◀' : '▶'}
          </button>
        </div>
        
        <nav className="p-4">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 p-3 rounded-lg mb-2 transition-colors ${
                location.pathname === item.path
                  ? 'bg-blue-600'
                  : 'hover:bg-slate-700'
              }`}
            >
              <span>{item.icon}</span>
              <span className={`${!sidebarOpen && 'hidden'}`}>{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="absolute bottom-0 w-full p-4 border-t border-slate-700">
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 p-3 rounded-lg hover:bg-red-600 w-full transition-colors"
          >
            <span>🚪</span>
            <span className={`${!sidebarOpen && 'hidden'}`}>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <header className="bg-white shadow-sm p-4">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold text-gray-800">
              {navItems.find(item => item.path === location.pathname)?.label || 'FlowRecover'}
            </h2>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">Demo User</span>
            </div>
          </div>
        </header>

        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export default Layout
