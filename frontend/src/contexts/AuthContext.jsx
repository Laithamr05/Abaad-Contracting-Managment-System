import { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in on mount
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      // You'll need to implement an endpoint to check current user
      // const response = await api.get('/auth/me')
      // setUser(response.data)
    } catch (error) {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    try {
      const response = await api.post('/api/login', { username, password })
      if (response.data.success) {
        setUser(response.data.user)
        return { success: true }
      } else {
        return { success: false, error: response.data.message || 'Login failed' }
      }
    } catch (error) {
      return { success: false, error: error.response?.data?.message || 'Login failed' }
    }
  }

  const logout = async () => {
    try {
      await api.post('/api/logout')
      setUser(null)
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  const signup = async (username, email, password, confirmPassword) => {
    try {
      const response = await api.post('/api/signup', {
        username,
        email,
        password,
        confirm_password: confirmPassword
      })
      return { success: true, message: response.data.message }
    } catch (error) {
      return { success: false, error: error.response?.data?.message || 'Signup failed' }
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, signup }}>
      {children}
    </AuthContext.Provider>
  )
}
