import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
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
      <div className="navbar-content">
        <button 
          className="menu-hamburger"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        <div className="navbar-logo">
          <img 
            src="/static/images/sumo-logo.png" 
            alt="SUMO" 
            className="logo-img"
          />
        </div>

        <a 
          href="tel:077-806-6300"
          className="call-now-btn"
        >
          <i className="fas fa-phone"></i>
          <span>{language === 'he' ? 'חייג' : 'Call'}</span>
        </a>

        <ul className={`navbar-menu ${mobileMenuOpen ? 'active' : ''}`}>
          <li><a href="#about" onClick={(e) => handleNavClick(e, '#about')}>{t.about}</a></li>
          <li><Link to="/menu" onClick={() => setMobileMenuOpen(false)}>{t.menu}</Link></li>
          <li><a href="#gallery" onClick={(e) => handleNavClick(e, '#gallery')}>{t.gallery}</a></li>
          <li><a href="#reservations" onClick={(e) => handleNavClick(e, '#reservations')}>{t.reservations}</a></li>
          <li><a href="#contact" onClick={(e) => handleNavClick(e, '#contact')}>{t.contact}</a></li>
          <li className="language-selector-mobile">
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
          </li>
        </ul>
      </div>
    </nav>
  )
}

export default Navbar