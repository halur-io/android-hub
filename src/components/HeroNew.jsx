import React, { useState } from 'react'
import './HeroNew.css'
import BranchModal from './BranchModal'

const HeroNew = ({ language }) => {
  const [modalOpen, setModalOpen] = useState(false)
  const [selectedAction, setSelectedAction] = useState(null)
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

  const handleActionClick = (actionType) => {
    setSelectedAction(actionType)
    setModalOpen(true)
  }

  return (
    <section className="hero-new">
      <div className="hero-background">
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

          <div className="hero-main-actions">
            <button 
              className="main-action-btn"
              onClick={() => handleActionClick('takeaway')}
            >
              <i className="fas fa-phone"></i>
              <span>{t.takeaway}</span>
            </button>
            
            <button 
              className="main-action-btn primary"
              onClick={() => handleActionClick('delivery')}
            >
              <i className="fab fa-whatsapp"></i>
              <span>{t.delivery}</span>
            </button>
            
            <button 
              className="main-action-btn"
              onClick={() => handleActionClick('reservations')}
            >
              <i className="fas fa-calendar-check"></i>
              <span>{t.reservations}</span>
            </button>
          </div>
        </div>
      </div>

      <div className="scroll-indicator">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </div>

      <BranchModal 
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        actionType={selectedAction}
        language={language}
      />
    </section>
  )
}

export default HeroNew