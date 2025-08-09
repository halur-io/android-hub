import React, { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import HeroNew from './components/HeroNew'
import SpecialOffers from './components/SpecialOffers'
import About from './components/About'
import MenuNew from './components/MenuNew'
import InstagramFeed from './components/InstagramFeed'
import Contact from './components/Contact'
import Footer from './components/Footer'
import './App.css'

function App() {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('language') || 'he'
  })

  useEffect(() => {
    localStorage.setItem('language', language)
    document.documentElement.setAttribute('dir', language === 'he' ? 'rtl' : 'ltr')
    document.documentElement.setAttribute('lang', language)
  }, [language])

  return (
    <div className="app">
      <Navbar language={language} setLanguage={setLanguage} />
      <HeroNew language={language} />
      <SpecialOffers language={language} />
      <About language={language} />
      <MenuNew language={language} />
      <InstagramFeed language={language} />
      <Contact language={language} />
      <Footer language={language} />
    </div>
  )
}

export default App