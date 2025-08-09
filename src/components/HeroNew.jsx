import React from 'react'
import './HeroNew.css'

const HeroNew = ({ language }) => {
  const translations = {
    he: {
      title: 'סומו',
      subtitle: 'מטבח אסיאתי',
      tagline: 'חווית טעמים אסייתית אותנטית',
      orderNow: 'הזמינו עכשיו',
      reserveTable: 'שריינו שולחן',
      viewMenu: 'צפו בתפריט',
      takeaway: 'TA',
      delivery: 'משלוח'
    },
    en: {
      title: 'SUMO',
      subtitle: 'Asian Kitchen',
      tagline: 'Authentic Asian Taste Experience',
      orderNow: 'Order Now',
      reserveTable: 'Reserve Table',
      viewMenu: 'View Menu',
      takeaway: 'TA',
      delivery: 'Delivery'
    }
  }

  const t = translations[language]

  return (
    <section className="hero-new">
      <div className="hero-background">
        <div className="hero-overlay"></div>
      </div>
      
      <div className="hero-content-new">
        <div className="hero-text">
          <h1 className="hero-title-new">{t.title}</h1>
          <h2 className="hero-subtitle-new">{t.subtitle}</h2>
          <p className="hero-tagline">{t.tagline}</p>
        </div>

        <div className="hero-actions">
          <a href="tel:077-806-6300" className="hero-card takeaway-card">
            <div className="card-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20 20H4a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v10a2 2 0 01-2 2z"/>
                <polyline points="7 10 12 15 17 10"/>
              </svg>
            </div>
            <h3>{t.takeaway}</h3>
            <p>077-806-6300</p>
          </a>

          <a href="https://wa.me/972778066300" className="hero-card delivery-card">
            <div className="card-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="1" y="3" width="15" height="13"></rect>
                <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
                <circle cx="5.5" cy="18.5" r="2.5"></circle>
                <circle cx="18.5" cy="18.5" r="2.5"></circle>
              </svg>
            </div>
            <h3>{t.delivery}</h3>
            <p>WhatsApp</p>
          </a>

          <a href="#reservations" className="hero-card reserve-card">
            <div className="card-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
            </div>
            <h3>{t.reserveTable}</h3>
            <p>{t.viewMenu}</p>
          </a>
        </div>
      </div>

      <div className="scroll-indicator">
        <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </div>
    </section>
  )
}

export default HeroNew