import React, { useState, useEffect } from 'react'
import './Navbar.css'

const Navbar = ({ language, setLanguage }) => {
  const [scrolled, setScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const translations = {
    he: {
      about: 'אודות',
      menu: 'תפריט',
      gallery: 'גלריה',
      reservations: 'הזמנות',
      contact: 'צור קשר'
    },
    en: {
      about: 'About',
      menu: 'Menu',
      gallery: 'Gallery',
      reservations: 'Reservations',
      contact: 'Contact'
    }
  }

  const t = translations[language]

  const handleNavClick = (e, href) => {
    e.preventDefault()
    setMobileMenuOpen(false)
    const element = document.querySelector(href)
    if (element) {
      const offset = 80
      const elementPosition = element.getBoundingClientRect().top
      const offsetPosition = elementPosition + window.pageYOffset - offset
      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      })
    }
  }

  return (
    <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
      <div className="container">
        <div className="navbar-content">
          <div className="navbar-logo">
            <img 
              src="/static/images/sumo-logo.png" 
              alt="SUMO" 
              className="logo-img"
            />
          </div>

          <ul className={`navbar-menu ${mobileMenuOpen ? 'active' : ''}`}>
            <li><a href="#about" onClick={(e) => handleNavClick(e, '#about')}>{t.about}</a></li>
            <li><a href="#menu" onClick={(e) => handleNavClick(e, '#menu')}>{t.menu}</a></li>
            <li><a href="#gallery" onClick={(e) => handleNavClick(e, '#gallery')}>{t.gallery}</a></li>
            <li><a href="#reservations" onClick={(e) => handleNavClick(e, '#reservations')}>{t.reservations}</a></li>
            <li><a href="#contact" onClick={(e) => handleNavClick(e, '#contact')}>{t.contact}</a></li>
          </ul>

          <div className="navbar-actions">
            <div className="contact-buttons">
              <a 
                href="https://wa.me/972778066300" 
                target="_blank" 
                rel="noopener noreferrer"
                className="contact-btn whatsapp-btn"
                aria-label="WhatsApp"
              >
                <i className="fab fa-whatsapp"></i>
              </a>
              <a 
                href="tel:077-806-6300"
                className="contact-btn phone-btn"
                aria-label="Phone"
              >
                <i className="fas fa-phone"></i>
              </a>
            </div>

            <div className="language-selector">
              <button 
                className={`lang-btn ${language === 'he' ? 'active' : ''}`}
                onClick={() => setLanguage('he')}
              >
                עב
              </button>
              <button 
                className={`lang-btn ${language === 'en' ? 'active' : ''}`}
                onClick={() => setLanguage('en')}
              >
                EN
              </button>
            </div>

            <button 
              className="mobile-menu-btn"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle menu"
            >
              <span></span>
              <span></span>
              <span></span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar