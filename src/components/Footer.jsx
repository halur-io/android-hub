import React from 'react'
import './Footer.css'

const Footer = ({ language }) => {
  const translations = {
    he: {
      rights: 'כל הזכויות שמורות',
      followUs: 'עקבו אחרינו'
    },
    en: {
      rights: 'All rights reserved',
      followUs: 'Follow us'
    }
  }

  const t = translations[language]

  const quickActionTranslations = {
    he: {
      call: 'התקשרו',
      order: 'הזמינו',
      directions: 'הגיעו'
    },
    en: {
      call: 'Call Us',
      order: 'Order Now',
      directions: 'Get Directions'
    }
  }

  const qt = quickActionTranslations[language]

  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-quick-actions">
          <a href="tel:+972778066300" className="footer-action-btn">
            <i className="fas fa-phone"></i>
            <span>{qt.call}</span>
          </a>
          <a href="https://wa.me/972778066300" className="footer-action-btn">
            <i className="fas fa-shopping-cart"></i>
            <span>{qt.order}</span>
          </a>
          <a href="https://waze.com" className="footer-action-btn">
            <i className="fas fa-map-marker-alt"></i>
            <span>{qt.directions}</span>
          </a>
        </div>
        
        <div className="footer-content">
          <div className="footer-logo">
            <img 
              src="/static/images/sumo-logo.png" 
              alt="SUMO" 
              className="footer-logo-img"
            />
          </div>
          
          <div className="footer-info">
            <p>&copy; 2024 SUMO Asian Kitchen. {t.rights}.</p>
          </div>
          
          <div className="footer-social">
            <p>{t.followUs}:</p>
            <div className="social-links">
              <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" aria-label="Facebook"><i className="fab fa-facebook"></i></a>
              <a href="https://instagram.com" target="_blank" rel="noopener noreferrer" aria-label="Instagram"><i className="fab fa-instagram"></i></a>
              <a href="https://wa.me/972778066300" target="_blank" rel="noopener noreferrer" aria-label="WhatsApp"><i className="fab fa-whatsapp"></i></a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer