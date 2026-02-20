import { createContext, useContext, useState, ReactNode } from 'react'

interface AuthContextType {
  token: string | null
  role: string | null
  nom: string | null
  login: (token: string, role: string, nom: string) => void
  logout: () => void
}

const defaultValue: AuthContextType = {
  token: null,
  role: null,
  nom: null,
  login: () => {},
  logout: () => {}
}

const AuthContext = createContext<AuthContextType>(defaultValue)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [role, setRole]   = useState<string | null>(localStorage.getItem('role'))
  const [nom, setNom]     = useState<string | null>(localStorage.getItem('nom'))

  const login = (t: string, r: string, n: string) => {
    localStorage.setItem('token', t)
    localStorage.setItem('role', r)
    localStorage.setItem('nom', n)
    setToken(t)
    setRole(r)
    setNom(n)
  }

  const logout = () => {
    localStorage.clear()
    setToken(null)
    setRole(null)
    setNom(null)
  }

  return (
    <AuthContext.Provider value={{ token, role, nom, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)