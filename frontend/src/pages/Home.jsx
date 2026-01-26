import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useLanguage } from '../contexts/LanguageContext'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

const Home = () => {
  const { t } = useLanguage()
  const { user } = useAuth()
  const [stats, setStats] = useState({
    branch_count: 0,
    employee_count: 0,
    project_count: 0,
    client_count: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/stats')
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <section className="hero-section hero-light py-5">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-8 mx-auto text-center">
              <h1 className="display-4 fw-bold mb-4">{t('hero-title')}</h1>
              <p className="lead mb-4">{t('home-hero-text')}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-5 bg-light">
        <div className="container">
          <div className="row g-4">
            <div className="col-md-3 col-6">
              <div className="text-center">
                <h2 className="display-5 fw-bold text-primary mb-2" aria-label={`${stats.branch_count || 0} ${t('stats-branches-label')}`}>
                  {loading ? '...' : (stats.branch_count || 0)}
                </h2>
                <p className="text-muted mb-0">{t('stats-branches-label')}</p>
              </div>
            </div>
            <div className="col-md-3 col-6">
              <div className="text-center">
                <h2 className="display-5 fw-bold text-primary mb-2" aria-label={`${stats.employee_count || 0} ${t('stats-employees-label')}`}>
                  {loading ? '...' : (stats.employee_count || 0)}
                </h2>
                <p className="text-muted mb-0">{t('stats-employees-label')}</p>
              </div>
            </div>
            <div className="col-md-3 col-6">
              <div className="text-center">
                <h2 className="display-5 fw-bold text-primary mb-2" aria-label={`${stats.project_count || 0} ${t('stats-projects-label')}`}>
                  {loading ? '...' : (stats.project_count || 0)}
                </h2>
                <p className="text-muted mb-0">{t('stats-projects-label')}</p>
              </div>
            </div>
            <div className="col-md-3 col-6">
              <div className="text-center">
                <h2 className="display-5 fw-bold text-primary mb-2" aria-label={`${stats.client_count || 0} ${t('stats-clients-label')}`}>
                  {loading ? '...' : (stats.client_count || 0)}
                </h2>
                <p className="text-muted mb-0">{t('stats-clients-label')}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {user?.is_admin && (
        <section className="py-5">
          <div className="container">
            <h2 className="text-center mb-5">{t('home-management-title')}</h2>
            <div className="row g-4">
              <div className="col-md-4">
                <div className="card h-100 border-0 shadow-sm text-center">
                  <div className="card-body p-4">
                    <i className="bi bi-building fs-1 text-primary mb-3"></i>
                    <h5 className="card-title">{t('home-management-projects-title')}</h5>
                    <p className="text-muted">{t('home-management-projects-text')}</p>
                    <Link to="/projects" className="btn btn-primary">
                      {t('home-management-projects-link')}
                    </Link>
                  </div>
                </div>
              </div>
              <div className="col-md-4">
                <div className="card h-100 border-0 shadow-sm text-center">
                  <div className="card-body p-4">
                    <i className="bi bi-people fs-1 text-primary mb-3"></i>
                    <h5 className="card-title">{t('home-management-employees-title')}</h5>
                    <p className="text-muted">{t('home-management-employees-text')}</p>
                    <Link to="/employees" className="btn btn-primary">
                      {t('home-management-employees-link')}
                    </Link>
                  </div>
                </div>
              </div>
              <div className="col-md-4">
                <div className="card h-100 border-0 shadow-sm text-center">
                  <div className="card-body p-4">
                    <i className="bi bi-graph-up fs-1 text-primary mb-3"></i>
                    <h5 className="card-title">{t('home-management-reports-title')}</h5>
                    <p className="text-muted">{t('home-management-reports-text')}</p>
                    <Link to="/all_queries" className="btn btn-primary">
                      {t('home-management-reports-link')}
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}
    </>
  )
}

export default Home
