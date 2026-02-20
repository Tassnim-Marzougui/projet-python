import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './AuthContext'
import Login from './pages/Login'
import Register from './pages/Register'
import DashboardModerateur from './pages/DashboardModerateur'
import DashboardAdmin from './pages/DashboardAdmin'
import { ReactElement } from 'react'

function ProtectedRoute({ children, role }: { children: ReactElement, role?: string }) {
  const { token, role: userRole } = useAuth()
  if (!token) return <Navigate to="/login" />
  if (role && userRole !== role) return <Navigate to="/login" />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/moderateur/dashboard" element={
        <ProtectedRoute role="moderateur">
          <DashboardModerateur />
        </ProtectedRoute>
      } />
      <Route path="/admin/dashboard" element={
        <ProtectedRoute role="admin">
          <DashboardAdmin />
        </ProtectedRoute>
      } />
    </Routes>
  )
}