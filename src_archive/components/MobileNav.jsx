import React, { useState, useEffect } from 'react'
import './MobileNav.css'

const MobileNav = ({ language }) => {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      // Show mobile nav when scrolled past hero section
      setIsVisible(window.scrollY > 100)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const scrollToSection = (sectionId) => {
    const element = document.querySelector(sectionId)
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

  const translations = {
    he: {
      menu: 'תפריט',
      reservations: 'הזמנות',
      call: 'חייג',
      location: 'מיקום'
    },
    en: {
      menu: 'Menu',
      reservations: 'Reservations', 
      call: 'Call',
      location: 'Location'
    }
  }

  const t = translations[language]

  if (!isVisible) return null

  return (
    <div className="mobile-nav-bottom">
      <button 
        className="mobile-nav-btn"
        onClick={() => scrollToSection('#menu')}
      >
        <i className="fas fa-utensils"></i>
        <span>{t.menu}</span>
      </button>
      
      <button 
        className="mobile-nav-btn"
        onClick={() => scrollToSection('#reservations')}
      >
        <i className="fas fa-calendar-plus"></i>
        <span>{t.reservations}</span>
      </button>
      
      <a 
        href="tel:077-806-6300"
        className="mobile-nav-btn mobile-nav-call"
      >
        <i className="fas fa-phone"></i>
        <span>{t.call}</span>
      </a>
      
      <button 
        className="mobile-nav-btn"
        onClick={() => scrollToSection('#contact')}
      >
        <i className="fas fa-map-marker-alt"></i>
        <span>{t.location}</span>
      </button>
    </div>
  )
}

export default MobileNav