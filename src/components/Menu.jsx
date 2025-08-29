import React, { useState, useEffect } from 'react'
import { api } from '../services/api'
import './Menu.css'

const Menu = ({ language }) => {
  const [menuData, setMenuData] = useState([])
  const [activeCategory, setActiveCategory] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchMenu = async () => {
      try {
        const data = await api.getMenu()
        setMenuData(data)
        if (data.length > 0) {
          setActiveCategory(data[0].id)
        }
      } catch (error) {
        console.error('Error fetching menu:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchMenu()
  }, [])

  const translations = {
    he: {
      title: 'התפריט שלנו',
      subtitle: 'מבחר מנות אסייתיות מעולות',
      currency: '₪',
      loading: 'טוען תפריט...',
      noItems: 'אין פריטים זמינים'
    },
    en: {
      title: 'Our Menu',
      subtitle: 'Selection of excellent Asian dishes',
      currency: 'NIS',
      loading: 'Loading menu...',
      noItems: 'No items available'
    }
  }

  const t = translations[language]
  const activeMenuCategory = menuData.find(cat => cat.id === activeCategory)

  if (loading) {
    return (
      <section id="menu" className="menu-section">
        <div className="container">
          <h2 className="section-title">{t.title}</h2>
          <p className="section-subtitle">{t.loading}</p>
        </div>
      </section>
    )
  }

  return (
    <section id="menu" className="menu-section">
      <div className="container">
        <h2 className="section-title">{t.title}</h2>
        <p className="section-subtitle">{t.subtitle}</p>

        {menuData.length > 0 && (
          <>
            <div className="menu-tabs">
              {menuData.map(category => (
                <button
                  key={category.id}
                  className={`menu-tab ${activeCategory === category.id ? 'active' : ''}`}
                  onClick={() => setActiveCategory(category.id)}
                >
                  {language === 'he' ? category.name_he : category.name_en}
                </button>
              ))}
            </div>

            <div className="menu-items">
              {activeMenuCategory?.items?.length > 0 ? (
                activeMenuCategory.items.map((item, index) => (
                  <div key={item.id} className="menu-item fade-in-up">
                    <div className="menu-item-header">
                      <h3 className="menu-item-name">
                        {language === 'he' ? item.name_he : item.name_en}
                      </h3>
                      {item.base_price && (
                        <span className="menu-item-price">
                          {t.currency}{item.base_price}
                        </span>
                      )}
                    </div>
                    
                    {(item.description_he || item.description_en) && (
                      <p className="menu-item-description">
                        {language === 'he' ? item.description_he : item.description_en}
                      </p>
                    )}

                    {item.dietary_properties.length > 0 && (
                      <div className="menu-item-properties">
                        {item.dietary_properties.map(prop => (
                          <span
                            key={prop.id}
                            className="dietary-property"
                            style={{ color: prop.color }}
                            title={language === 'he' ? prop.name_he : prop.name_en}
                          >
                            <i className={`fas fa-${prop.icon}`}></i>
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <p className="no-items">{t.noItems}</p>
              )}
            </div>
          </>
        )}
      </div>
    </section>
  )
}

export default Menu