import React, { useState } from 'react'
import './Menu.css'

const Menu = ({ language }) => {
  const [activeCategory, setActiveCategory] = useState('sushi')

  const translations = {
    he: {
      title: 'התפריט שלנו',
      subtitle: 'מבחר מנות אסייתיות מעולות',
      categories: {
        sushi: 'סושי',
        thai: 'תאילנדי',
        korean: 'קוריאני',
        vietnamese: 'וייטנאמי'
      },
      currency: '₪'
    },
    en: {
      title: 'Our Menu',
      subtitle: 'Selection of excellent Asian dishes',
      categories: {
        sushi: 'Sushi',
        thai: 'Thai',
        korean: 'Korean',
        vietnamese: 'Vietnamese'
      },
      currency: 'NIS'
    }
  }

  const menuItems = {
    sushi: [
      { name: { he: 'סלמון רול', en: 'Salmon Roll' }, price: 42 },
      { name: { he: 'טונה רול', en: 'Tuna Roll' }, price: 48 },
      { name: { he: 'קליפורניה רול', en: 'California Roll' }, price: 38 },
      { name: { he: 'ספיישל רול', en: 'Special Roll' }, price: 55 }
    ],
    thai: [
      { name: { he: 'פאד תאי', en: 'Pad Thai' }, price: 52 },
      { name: { he: 'תום יאם', en: 'Tom Yum' }, price: 38 },
      { name: { he: 'קארי ירוק', en: 'Green Curry' }, price: 58 },
      { name: { he: 'סום טאם', en: 'Som Tam' }, price: 35 }
    ],
    korean: [
      { name: { he: 'ביבימבאפ', en: 'Bibimbap' }, price: 48 },
      { name: { he: 'בולגוגי', en: 'Bulgogi' }, price: 62 },
      { name: { he: 'קימצ\'י', en: 'Kimchi' }, price: 18 },
      { name: { he: 'ג\'אפצ\'ה', en: 'Japchae' }, price: 42 }
    ],
    vietnamese: [
      { name: { he: 'פו', en: 'Pho' }, price: 45 },
      { name: { he: 'באן מי', en: 'Banh Mi' }, price: 38 },
      { name: { he: 'גוי קון', en: 'Goi Cuon' }, price: 32 },
      { name: { he: 'בון בו הואה', en: 'Bun Bo Hue' }, price: 48 }
    ]
  }

  const t = translations[language]

  return (
    <section id="menu" className="menu-section">
      <div className="container">
        <h2 className="section-title">{t.title}</h2>
        <p className="section-subtitle">{t.subtitle}</p>

        <div className="menu-tabs">
          {Object.keys(t.categories).map(category => (
            <button
              key={category}
              className={`menu-tab ${activeCategory === category ? 'active' : ''}`}
              onClick={() => setActiveCategory(category)}
            >
              {t.categories[category]}
            </button>
          ))}
        </div>

        <div className="menu-items">
          {menuItems[activeCategory].map((item, index) => (
            <div key={index} className="menu-item fade-in-up">
              <h3 className="menu-item-name">{item.name[language]}</h3>
              <span className="menu-item-price">{t.currency}{item.price}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Menu