import { Link } from 'react-router-dom'
import { useLanguage } from '../contexts/LanguageContext'
import { useAuth } from '../contexts/AuthContext'
import SafeImage from './SafeImage'

const Footer = () => {
  const { t } = useLanguage()
  const { user } = useAuth()

  return (
    <footer className="footer text-white py-5 mt-5">
      <div className="container">
        <div className="row gy-4 align-items-center">
          <div className="col-md-4">
            <div className="d-flex align-items-center mb-3">
              <SafeImage 
                src="/static/images/logo.png" 
                alt="Abaad Contracting Logo" 
                className="navbar-logo me-2"
                height={40}
                maxWidth={160}
                objectFit="contain"
                lazy={false}
              />
              <div>
                <h5 className="mb-0">{t('footer-brand')}</h5>
                <small className="text-muted">{t('footer-tagline')}</small>
              </div>
            </div>
            <p className="mb-1 small text-muted">
              <span>{t('footer-address-line1')}</span><br />
              <span>{t('footer-address-line2')}</span>
            </p>
            <p className="mb-1 small">
              <span className="text-muted">{t('footer-phone-label')}</span>
              <span dir="ltr"> +970 22989898</span>
            </p>
            <p className="mb-0 small">
              <span className="text-muted">{t('footer-email-label')}</span>
              {' '}info@abaad.ps
            </p>
          </div>

          <div className="col-md-4">
            <h5>{t('footer-quick-links')}</h5>
            <ul className="list-unstyled small mb-0">
              <li><Link to="/" className="text-decoration-none text-muted">{t('footer-home')}</Link></li>
              <li><Link to="/about" className="text-decoration-none text-muted">{t('footer-about')}</Link></li>
              {user?.is_admin && (
                <>
                  <li><Link to="/projects" className="text-decoration-none text-muted">{t('footer-projects')}</Link></li>
                  <li><Link to="/all_queries" className="text-decoration-none text-muted">{t('footer-reports')}</Link></li>
                </>
              )}
            </ul>
          </div>

          <div className="col-md-4">
            <h5>{t('footer-working-with-us')}</h5>
            <p className="small text-muted mb-3">{t('footer-working-text')}</p>
            <div className="d-flex flex-wrap gap-2">
              <a href="tel:+97022989898" className="btn btn-sm btn-primary">{t('footer-call')}</a>
              <a href="mailto:info@abaad.ps" className="btn btn-sm btn-outline-light">{t('footer-email')}</a>
            </div>
          </div>
        </div>

        <hr className="border-secondary my-4" />

        <div className="d-flex flex-column flex-md-row justify-content-between align-items-center">
          <p className="small mb-2 mb-md-0 text-muted">{t('footer-copyright')}</p>
          <p className="small mb-0 text-muted">{t('footer-designed-for')}</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
