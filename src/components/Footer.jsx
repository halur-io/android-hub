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

  return (
    <footer className="footer">
      <div className="container">
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
              <a href="#" aria-label="Facebook"><i className="fab fa-facebook"></i></a>
              <a href="#" aria-label="Instagram"><i className="fab fa-instagram"></i></a>
              <a href="#" aria-label="WhatsApp"><i className="fab fa-whatsapp"></i></a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer