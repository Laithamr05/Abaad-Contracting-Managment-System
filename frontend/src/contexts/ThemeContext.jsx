import { createContext, useContext, useState, useEffect } from 'react'

const ThemeContext = createContext()

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    // Check localStorage first, then system preference
    const saved = localStorage.getItem('abaad-theme')
    if (saved) return saved
    
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark'
    }
    
    return 'light'
  })

  // Apply theme on mount and when it changes
  useEffect(() => {
    const body = document.body
    const html = document.documentElement
    
    if (theme === 'dark') {
      body.classList.add('dark-mode')
      html.setAttribute('data-theme', 'dark')
    } else {
      body.classList.remove('dark-mode')
      html.setAttribute('data-theme', 'light')
    }
    
    localStorage.setItem('abaad-theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}
