import React from 'react'
import './Hero.css'

const Hero = ({ language }) => {
  const translations = {
    he: {
      title: 'סומו',
      subtitle: 'מטבח אסייתי אותנטי',
      description: 'חוויה קולינרית ייחודית של טעמי אסיה',
      orderBtn: 'הזמן עכשיו',
      reserveBtn: 'שריין שולחן'
    },
    en: {
      title: 'SUMO',
      subtitle: 'Authentic Asian Kitchen',
      description: 'A unique culinary experience of Asian flavors',
      orderBtn: 'Order Now',
      reserveBtn: 'Reserve Table'
    }
  }

  const t = translations[language]

  return (
    <section id="hero" className="hero-section">
      <div className="hero-background">
        <div className="hero-overlay"></div>
      </div>
      <div className="hero-content">
        <h1 className="hero-title fade-in-up">{t.title}</h1>
        <h2 className="hero-subtitle fade-in-up">{t.subtitle}</h2>
        <p className="hero-description fade-in-up">{t.description}</p>
        
        <div className="quick-actions fade-in-up">
          <a href="#reservations" className="action-btn">
            <i className="fas fa-calendar-check"></i>
            <span>{language === 'he' ? 'הזמנת שולחן' : 'Table Reservation'}</span>
          </a>
          <a href="tel:077-806-6300" className="action-btn">
            <i className="fas fa-shopping-bag"></i>
            <span>{language === 'he' ? 'טייק אוויי' : 'Take Away'}</span>
          </a>
          <a href="https://wa.me/972778066300?text=שלום, אני רוצה להזמין משלוח" className="action-btn">
            <i className="fas fa-motorcycle"></i>
            <span>{language === 'he' ? 'משלוח' : 'Delivery'}</span>
          </a>
        </div>
      </div>
    </section>
  )
}

export default Hero