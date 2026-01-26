import { useLanguage } from '../contexts/LanguageContext'
import SafeImage from '../components/SafeImage'

const About = () => {
  const { t } = useLanguage()

  const teamMembers = [
    {
      name: t('about-team-osama-name'),
      role: t('about-team-osama-role'),
      image: '/static/images/team/Osama Amro.webp'
    },
    {
      name: t('about-team-mohammad-name'),
      role: t('about-team-mohammad-role'),
      image: '/static/images/team/Mohammad Amro.webp'
    },
    {
      name: t('about-team-zaid-name'),
      role: t('about-team-zaid-role'),
      image: '/static/images/team/Zaid Amro.webp'
    },
    {
      name: t('about-team-ammar-name'),
      role: t('about-team-ammar-role'),
      image: '/static/images/team/Ammar Amro.webp'
    }
  ]

  return (
    <>
      <section className="hero-section hero-light py-5">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-8 mx-auto text-center">
              <h1 className="display-4 fw-bold mb-4">{t('hero-title')}</h1>
              <p className="lead mb-4">{t('about-hero-text')}</p>
              <p className="mb-0">{t('about-hero-extra')}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-5">
        <div className="container">
          <div className="row g-4 mb-5">
            <div className="col-md-4">
              <div className="card h-100 border-0 shadow-sm">
                <div className="card-body text-center p-4">
                  <i className="bi bi-award fs-1 text-primary mb-3" aria-hidden="true"></i>
                  <h3 className="h5 mb-3">{t('about-deep-rooted')}</h3>
                  <p className="text-muted mb-0">{t('about-deep-rooted-text')}</p>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card h-100 border-0 shadow-sm">
                <div className="card-body text-center p-4">
                  <i className="bi bi-shield-check fs-1 text-primary mb-3" aria-hidden="true"></i>
                  <h3 className="h5 mb-3">{t('about-safety')}</h3>
                  <p className="text-muted mb-0">{t('about-safety-text')}</p>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card h-100 border-0 shadow-sm">
                <div className="card-body text-center p-4">
                  <i className="bi bi-trophy fs-1 text-primary mb-3" aria-hidden="true"></i>
                  <h3 className="h5 mb-3">{t('about-leadership')}</h3>
                  <p className="text-muted mb-0">{t('about-leadership-text')}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="row mb-5">
            <div className="col-lg-8 mx-auto text-center">
              <h2 className="mb-4">{t('about-partners')}</h2>
              <p className="text-muted lead">{t('about-partners-text')}</p>
            </div>
          </div>

          <div className="row">
            <div className="col-12 text-center mb-5">
              <h2 className="mb-4">{t('about-team')}</h2>
              <p className="text-muted lead mb-5">{t('about-team-text')}</p>
            </div>
          </div>

          <div className="row g-4 justify-content-center">
            {teamMembers.map((member, index) => (
              <div key={index} className="col-md-6 col-lg-3">
                <div className="team-card">
                  <SafeImage
                    src={member.image}
                    alt={`${member.name} - ${member.role}`}
                    aspectRatio="3/4"
                    objectFit="cover"
                    className="w-100"
                    fallbackSrc="/static/images/logo.png"
                  />
                  <h6 className="mb-1">{member.name}</h6>
                  <small className="text-muted">{member.role}</small>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  )
}

export default About
