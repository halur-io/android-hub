import React from 'react'
import './HeroNew.css'

const HeroNew = ({ language }) => {
  const translations = {
    he: {
      title: 'סומו',
      subtitle: 'מטבח אסיאתי',
      welcome: 'ברוכים הבאים לסומו',
      divider: '|',
      description: 'מטבח אסייתי עשיר, טרי ואיכותי',
      subdescription: 'מגוון מנות סושי מיוחדות, מוקפצים, קארי ומגוון מנות מהמזרח',
      quality: 'אנו מקפידים על שימוש בחומרי הגלם האיכותיים והטריים ביותר',
      takeaway: 'Take Away',
      delivery: 'משלוח',
      reservations: 'הזמנות',
      branches: 'הסניפים שלנו',
      rama: 'ראמה',
      karmiel: 'כרמיאל'
    },
    en: {
      title: 'SUMO',
      subtitle: 'Asian Kitchen',
      welcome: 'Welcome to Sumo',
      divider: '|',
      description: 'Rich, fresh and quality Asian cuisine',
      subdescription: 'A variety of special sushi, stir-fries, curries and Eastern dishes',
      quality: 'We use only the highest quality and freshest ingredients',
      takeaway: 'Take Away',
      delivery: 'Delivery',
      reservations: 'Reservations',
      branches: 'Our Branches',
      rama: 'Rama',
      karmiel: 'Karmiel'
    }
  }

  const t = translations[language]

  return (
    <section className="hero-new">
      <div className="hero-background">
        <video 
          className="hero-video"
          autoPlay 
          muted 
          loop 
          playsInline
        >
          <source src="/static/videos/sushi-preparation.mp4" type="video/mp4" />
          {/* Fallback for browsers that don't support video */}
          Your browser does not support the video tag.
        </video>
        <div className="hero-overlay"></div>
      </div>
      
      <div className="hero-content-new">
        <div className="hero-welcome-section">
          <div className="logo-container">
            <img src="/static/images/sumo-logo.png" alt="Sumo Logo" className="hero-logo" />
          </div>
          
          <div className="welcome-text">
            <h1>{t.welcome}</h1>
            <span className="divider">{t.divider}</span>
            <h2>{t.title} {t.subtitle}</h2>
            
            <p className="description">{t.description}</p>
            <p className="subdescription">{t.subdescription}</p>
            <p className="quality">{t.quality}</p>
          </div>

          <div className="hero-branches">
            <h3>{t.branches}</h3>
            <div className="branch-buttons">
              <button className="branch-btn">{t.rama}</button>
              <button className="branch-btn">{t.karmiel}</button>
            </div>
          </div>

          <div className="hero-actions-refined">
            <a href="tel:077-806-6300" className="action-btn">
              <span>{t.takeaway}</span>
            </a>
            <a href="https://wa.me/972778066300" className="action-btn primary">
              <span>{t.delivery}</span>
            </a>
            <a href="#contact" className="action-btn">
              <span>{t.reservations}</span>
            </a>
          </div>
        </div>
      </div>

      <div className="scroll-indicator">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </div>
    </section>
  )
}

export default HeroNew