import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import HeroNew from './components/HeroNew'
import About from './components/About'
import PhotoShowcase from './components/PhotoShowcase'
import Contact from './components/Contact'
import Footer from './components/Footer'
import MenuPage from './pages/MenuPage'
import './App.css'

function HomePage({ language, setLanguage }) {
  return (
    <div className="app">
      <Navbar language={language} setLanguage={setLanguage} />
      <HeroNew language={language} />
      <About language={language} />
      <PhotoShowcase language={language} />
      <Contact language={language} />
      <Footer language={language} />
    </div>
  )
}

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
    <Router>
      <Routes>
        <Route path="/" element={<HomePage language={language} setLanguage={setLanguage} />} />
        <Route path="/menu" element={<MenuPage />} />
      </Routes>
    </Router>
  )
}

export default App