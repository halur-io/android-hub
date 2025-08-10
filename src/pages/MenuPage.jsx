import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import './MenuPage.css'

const MenuPage = () => {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('language') || 'he'
  })

  useEffect(() => {
    document.documentElement.setAttribute('dir', language === 'he' ? 'rtl' : 'ltr')
    document.documentElement.setAttribute('lang', language)
  }, [language])

  const translations = {
    he: {
      title: 'התפריט שלנו',
      subtitle: 'מסע קולינרי אסייתי',
      backHome: 'חזרה לדף הבית',
      starters: 'ראשונות',
      sushi: 'סושי ורולים',
      wok: 'מנות ווק',
      soups: 'מרקים',
      desserts: 'קינוחים',
      drinks: 'משקאות',
      items: {
        starters: [
          { name: 'אדממה', price: '₪25', desc: 'פולי סויה מאודים עם מלח גס' },
          { name: 'גיוזה עוף', price: '₪35', desc: 'כיסוני בצק במילוי עוף וירקות' },
          { name: 'ספרינג רולס', price: '₪32', desc: 'אגרולים קריספיים עם ירקות' },
          { name: 'טמפורה ירקות', price: '₪38', desc: 'ירקות בציפוי טמפורה קריספי' }
        ],
        sushi: [
          { name: 'סשימי סלמון', price: '₪55', desc: '8 פרוסות סלמון טרי' },
          { name: 'ניגירי מיקס', price: '₪65', desc: '10 יחידות דגים מעורבים' },
          { name: 'רול קליפורניה', price: '₪48', desc: 'אבוקדו, מלפפון, סלמון' },
          { name: 'רול ספיישל', price: '₪68', desc: 'רול הבית המיוחד שלנו' }
        ],
        wok: [
          { name: 'פאד תאי', price: '₪58', desc: 'אטריות אורז עם עוף וירקות' },
          { name: 'נודלס עוף', price: '₪52', desc: 'אטריות ביצים עם עוף ברוטב סויה' },
          { name: 'בקר מונגולי', price: '₪78', desc: 'רצועות בקר ברוטב מונגולי' },
          { name: 'טופו ברוטב', price: '₪48', desc: 'טופו מוקפץ עם ירקות' }
        ],
        soups: [
          { name: 'מיסו', price: '₪28', desc: 'מרק סויה יפני מסורתי' },
          { name: 'טום יאם', price: '₪42', desc: 'מרק תאילנדי חריף' },
          { name: 'ראמן', price: '₪58', desc: 'מרק אטריות יפני עשיר' }
        ]
      }
    },
    en: {
      title: 'Our Menu',
      subtitle: 'An Asian Culinary Journey',
      backHome: 'Back to Home',
      starters: 'Starters',
      sushi: 'Sushi & Rolls',
      wok: 'Wok Dishes',
      soups: 'Soups',
      desserts: 'Desserts',
      drinks: 'Beverages',
      items: {
        starters: [
          { name: 'Edamame', price: '₪25', desc: 'Steamed soybeans with coarse salt' },
          { name: 'Chicken Gyoza', price: '₪35', desc: 'Dumplings filled with chicken and vegetables' },
          { name: 'Spring Rolls', price: '₪32', desc: 'Crispy rolls with vegetables' },
          { name: 'Vegetable Tempura', price: '₪38', desc: 'Vegetables in crispy tempura coating' }
        ],
        sushi: [
          { name: 'Salmon Sashimi', price: '₪55', desc: '8 pieces of fresh salmon' },
          { name: 'Nigiri Mix', price: '₪65', desc: '10 pieces of mixed fish' },
          { name: 'California Roll', price: '₪48', desc: 'Avocado, cucumber, salmon' },
          { name: 'Special Roll', price: '₪68', desc: 'Our special house roll' }
        ],
        wok: [
          { name: 'Pad Thai', price: '₪58', desc: 'Rice noodles with chicken and vegetables' },
          { name: 'Chicken Noodles', price: '₪52', desc: 'Egg noodles with chicken in soy sauce' },
          { name: 'Mongolian Beef', price: '₪78', desc: 'Beef strips in Mongolian sauce' },
          { name: 'Tofu Stir Fry', price: '₪48', desc: 'Stir-fried tofu with vegetables' }
        ],
        soups: [
          { name: 'Miso', price: '₪28', desc: 'Traditional Japanese soy soup' },
          { name: 'Tom Yum', price: '₪42', desc: 'Spicy Thai soup' },
          { name: 'Ramen', price: '₪58', desc: 'Rich Japanese noodle soup' }
        ]
      }
    }
  }

  const t = translations[language]

  const categories = [
    { id: 'starters', name: t.starters, icon: '🥟' },
    { id: 'sushi', name: t.sushi, icon: '🍱' },
    { id: 'wok', name: t.wok, icon: '🥘' },
    { id: 'soups', name: t.soups, icon: '🍜' }
  ]

  const [activeCategory, setActiveCategory] = useState('starters')

  return (
    <div className="menu-page">
      {/* Interactive Background */}
      <div className="interactive-bg">
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="wave"></div>
        <div className="wave"></div>
      </div>

      {/* Header */}
      <header className="menu-header">
        <Link to="/" className="back-button">
          <i className="fas fa-arrow-left"></i>
          <span>{t.backHome}</span>
        </Link>
        
        <div className="language-switch">
          <button 
            className={language === 'he' ? 'active' : ''} 
            onClick={() => setLanguage('he')}
          >
            עב
          </button>
          <button 
            className={language === 'en' ? 'active' : ''} 
            onClick={() => setLanguage('en')}
          >
            EN
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="menu-content">
        <div className="menu-title-section">
          <h1 className="menu-title">{t.title}</h1>
          <p className="menu-subtitle">{t.subtitle}</p>
        </div>

        {/* Category Tabs */}
        <div className="category-tabs">
          {categories.map(category => (
            <button
              key={category.id}
              className={`category-tab ${activeCategory === category.id ? 'active' : ''}`}
              onClick={() => setActiveCategory(category.id)}
            >
              <span className="category-icon">{category.icon}</span>
              <span className="category-name">{category.name}</span>
            </button>
          ))}
        </div>

        {/* Menu Items */}
        <div className="menu-items">
          {t.items[activeCategory]?.map((item, index) => (
            <div key={index} className="menu-item">
              <div className="item-header">
                <h3 className="item-name">{item.name}</h3>
                <span className="item-price">{item.price}</span>
              </div>
              <p className="item-desc">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default MenuPage