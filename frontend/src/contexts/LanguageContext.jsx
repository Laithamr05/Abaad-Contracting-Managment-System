import { createContext, useContext, useState, useEffect } from 'react'
import { translations } from '../utils/translations'

const LanguageContext = createContext()

export const useLanguage = () => {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider')
  }
  return context
}

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('abaad-lang') || 'en'
  })

  // Apply language settings
  useEffect(() => {
    const html = document.documentElement
    const body = document.body
    
    const target = language === 'ar' ? 'ar' : 'en'
    html.lang = target
    html.dir = target === 'ar' ? 'rtl' : 'ltr'
    body.classList.toggle('lang-ar', target === 'ar')
    
    localStorage.setItem('abaad-lang', target)
  }, [language])

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'en' ? 'ar' : 'en')
  }

  const t = (key) => {
    return translations[language]?.[key] || key
  }

  return (
    <LanguageContext.Provider value={{ language, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  )
}
