import React from 'react'
import './MenuNew.css'

const MenuNew = ({ language }) => {
  const translations = {
    he: {
      title: 'התפריט שלנו',
      subtitle: 'טעמים אסייתיים אותנטיים',
      sushi: 'סושי',
      thai: 'תאילנדי',
      korean: 'קוריאני',
      vietnamese: 'וייטנאמי',
      noodles: 'נודלס',
      salads: 'סלטים',
      orderNow: 'הזמן עכשיו',
      from: 'החל מ-',
      viewFull: 'תפריט מלא'
    },
    en: {
      title: 'Our Menu',
      subtitle: 'Authentic Asian Flavors',
      sushi: 'Sushi',
      thai: 'Thai',
      korean: 'Korean',
      vietnamese: 'Vietnamese',
      noodles: 'Noodles',
      salads: 'Salads',
      orderNow: 'Order Now',
      from: 'From ',
      viewFull: 'Full Menu'
    }
  }

  const t = translations[language]

  const menuCategories = [
    {
      name: t.sushi,
      description: language === 'he' ? 'רולים טריים ומיוחדים' : 'Fresh and special rolls',
      price: '38',
      icon: '🍣',
      color: '#FF6B6B'
    },
    {
      name: t.thai,
      description: language === 'he' ? 'מנות תאילנדיות מסורתיות' : 'Traditional Thai dishes',
      price: '42',
      icon: '🌶️',
      color: '#4ECDC4'
    },
    {
      name: t.korean,
      description: language === 'he' ? 'טעמי קוריאה האותנטיים' : 'Authentic Korean flavors',
      price: '48',
      icon: '🥘',
      color: '#FFD93D'
    },
    {
      name: t.vietnamese,
      description: language === 'he' ? 'מרקים ומנות וייטנאמיות' : 'Vietnamese soups and dishes',
      price: '45',
      icon: '🍜',
      color: '#95E1D3'
    },
    {
      name: t.noodles,
      description: language === 'he' ? 'מוקפצים ונודלס' : 'Stir fry and noodles',
      price: '35',
      icon: '🍝',
      color: '#FFA07A'
    },
    {
      name: t.salads,
      description: language === 'he' ? 'סלטים אסייתיים רעננים' : 'Fresh Asian salads',
      price: '28',
      icon: '🥗',
      color: '#98D8C8'
    }
  ]

  return (
    <section id="menu" className="menu-new">
      <div className="container">
        <h2 className="section-title">{t.title}</h2>
        <p className="section-subtitle">{t.subtitle}</p>

        <div className="menu-grid">
          {menuCategories.map((category, index) => (
            <div 
              key={index} 
              className="menu-card"
              style={{'--card-color': category.color}}
            >
              <div className="menu-card-header">
                <span className="menu-icon">{category.icon}</span>
                <h3 className="menu-card-title">{category.name}</h3>
              </div>
              <p className="menu-card-description">{category.description}</p>
              <div className="menu-card-footer">
                <span className="menu-price">
                  {t.from}₪{category.price}
                </span>
                <a href="tel:077-806-6300" className="menu-order-btn">
                  {t.orderNow}
                </a>
              </div>
            </div>
          ))}
        </div>

        <div className="menu-cta">
          <a href="#contact" className="view-full-menu">
            {t.viewFull}
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </a>
        </div>
      </div>
    </section>
  )
}

export default MenuNew