import { Link, useNavigate } from 'react-router-dom'
import { useTheme } from '../contexts/ThemeContext'
import { useLanguage } from '../contexts/LanguageContext'
import { useAuth } from '../contexts/AuthContext'
import SafeImage from './SafeImage'

const Navbar = () => {
  const { theme, toggleTheme } = useTheme()
  const { language, toggleLanguage, t } = useLanguage()
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container">
        <Link className="navbar-brand d-flex align-items-center" to="/">
          <SafeImage 
            src="/static/images/logo.png" 
            alt="Abaad Contracting Logo" 
            className="navbar-logo"
            height={40}
            maxWidth={160}
            objectFit="contain"
            lazy={false}
          />
          <span className="brand-text">Abaad Contracting</span>
        </Link>
        <button 
          className="navbar-toggler" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className={`navbar-nav ${language === 'ar' ? '' : 'ms-auto'} align-items-lg-center`}>
            <li className="nav-item">
              <Link className="nav-link" to="/">{t('nav-home')}</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/about">{t('nav-about')}</Link>
            </li>
            
            {user?.is_admin && (
              <>
                <li className="nav-item">
                  <Link className="nav-link" to="/projects">{t('nav-projects')}</Link>
                </li>
                <li className="nav-item dropdown">
                  <a 
                    className="nav-link dropdown-toggle" 
                    href="#" 
                    id="adminDropdown" 
                    role="button" 
                    data-bs-toggle="dropdown"
                    aria-expanded="false"
                    onClick={(e) => e.preventDefault()}
                  >
                    <i className="bi bi-gear" aria-hidden="true"></i> <span>{t('nav-database')}</span>
                  </a>
                  <ul className="dropdown-menu" aria-labelledby="adminDropdown">
                    <li><Link className="dropdown-item" to="/branches">Branches</Link></li>
                    <li><Link className="dropdown-item" to="/employees">Employees</Link></li>
                    <li><Link className="dropdown-item" to="/departments">Departments</Link></li>
                    <li><Link className="dropdown-item" to="/clients">Clients</Link></li>
                    <li><Link className="dropdown-item" to="/materials">Materials</Link></li>
                    <li><Link className="dropdown-item" to="/suppliers">Suppliers</Link></li>
                    <li><hr className="dropdown-divider" /></li>
                    <li><Link className="dropdown-item" to="/contracts">Contracts</Link></li>
                    <li><Link className="dropdown-item" to="/phases">Phases</Link></li>
                    <li><Link className="dropdown-item" to="/schedules">Schedules</Link></li>
                    <li><Link className="dropdown-item" to="/sales">Sales</Link></li>
                    <li><Link className="dropdown-item" to="/purchases">Purchases</Link></li>
                    <li><Link className="dropdown-item" to="/payments">Payments</Link></li>
                    <li><hr className="dropdown-divider" /></li>
                    <li><Link className="dropdown-item" to="/all_queries">{t('nav-reports')}</Link></li>
                  </ul>
                </li>
              </>
            )}

            {user ? (
              <li className="nav-item dropdown">
                <a 
                  className="nav-link dropdown-toggle" 
                  href="#" 
                  id="userDropdown" 
                  role="button" 
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                  onClick={(e) => e.preventDefault()}
                >
                  <i className="bi bi-person-circle" aria-hidden="true"></i> <span>{user.username}</span>
                </a>
                <ul className={`dropdown-menu ${language === 'ar' ? 'dropdown-menu-start' : 'dropdown-menu-end'}`} aria-labelledby="userDropdown">
                  <li>
                    <button className="dropdown-item" onClick={handleLogout}>
                      {t('nav-logout')}
                    </button>
                  </li>
                </ul>
              </li>
            ) : (
              <>
                <li className="nav-item">
                  <Link className="nav-link" to="/login">{t('nav-login')}</Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/signup">{t('nav-signup')}</Link>
                </li>
              </>
            )}

            <li className="nav-item mt-2 mt-lg-0 d-flex gap-2">
              <button 
                id="themeToggle"
                className="btn btn-sm btn-outline-light" 
                type="button"
                onClick={toggleTheme}
                aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                <i className={`bi bi-${theme === 'dark' ? 'sun' : 'moon'}`} aria-hidden="true"></i>
              </button>
              <button 
                id="langToggle"
                className="btn btn-sm btn-outline-light" 
                type="button"
                onClick={toggleLanguage}
                aria-label={`Switch to ${language === 'ar' ? 'English' : 'Arabic'}`}
              >
                <span id="langToggleLabel">{language === 'ar' ? 'EN' : 'AR'}</span>
              </button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
