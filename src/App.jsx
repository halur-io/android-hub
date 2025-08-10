import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import Navbar from './components/Navbar'
import HeroNew from './components/HeroNew'
import About from './components/About'
import PhotoShowcase from './components/PhotoShowcase'
import Contact from './components/Contact'
import Footer from './components/Footer'
import MenuPage from './pages/MenuPage'
import './App.css'

function HomePage({ language }) {
  return (
    <>
      <HeroNew language={language} />
      <About language={language} />
      <PhotoShowcase language={language} />
      <Contact language={language} />
      <Footer language={language} />
    </>
  )
}

function AppContent() {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('language') || 'he'
  })
  const location = useLocation()

  useEffect(() => {
    localStorage.setItem('language', language)
    document.documentElement.setAttribute('dir', language === 'he' ? 'rtl' : 'ltr')
    document.documentElement.setAttribute('lang', language)
  }, [language])

  // Show navbar only on home page
  const showNavbar = location.pathname === '/'

  return (
    <div className="app">
      {showNavbar && <Navbar language={language} setLanguage={setLanguage} />}
      <Routes>
        <Route path="/" element={<HomePage language={language} />} />
        <Route path="/menu" element={<MenuPage />} />
      </Routes>
    </div>
  )
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}

export default App