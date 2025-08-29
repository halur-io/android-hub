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
        <video 
          className="hero-video"
          autoPlay 
          loop 
          muted 
          playsInline
        >
          <source src="/static/videos/hero-bg.mov" type="video/quicktime" />
          <source src="/static/videos/hero-bg.mp4" type="video/mp4" />
        </video>
        <div className="hero-overlay"></div>
      </div>
      <div className="hero-content">
        <h1 className="hero-title fade-in-up">{t.title}</h1>
        <h2 className="hero-subtitle fade-in-up">{t.subtitle}</h2>
        <p className="hero-description fade-in-up">{t.description}</p>
      </div>
    </section>
  )
}

export default Hero