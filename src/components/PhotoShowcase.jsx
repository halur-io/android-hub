import React from 'react'
import './PhotoShowcase.css'

const PhotoShowcase = ({ language }) => {
  const translations = {
    he: {
      title: 'אווירה ומנות',
      subtitle: 'חוויה קולינרית ייחודית בסומו'
    },
    en: {
      title: 'Atmosphere & Dishes',
      subtitle: 'A unique culinary experience at Sumo'
    }
  }

  const t = translations[language]

  // Static photo showcase
  const photos = [
    { 
      id: 1, 
      alt: 'Restaurant Interior',
      category: 'אווירה',
      description: 'Restaurant ambiance'
    },
    { 
      id: 2, 
      alt: 'Signature Sushi Roll',
      category: 'סושי מיוחד',
      description: 'Chef special roll'
    },
    { 
      id: 3, 
      alt: 'Asian Fusion Dishes',
      category: 'מנות פיוז\'ן',
      description: 'Creative fusion cuisine'
    },
    { 
      id: 4, 
      alt: 'Fresh Sashimi',
      category: 'סשימי',
      description: 'Fresh daily selection'
    },
    { 
      id: 5, 
      alt: 'Wok Station',
      category: 'ווק',
      description: 'Live cooking experience'
    },
    { 
      id: 6, 
      alt: 'Dessert Selection',
      category: 'קינוחים',
      description: 'Sweet endings'
    }
  ]

  return (
    <section className="photo-showcase">
      <div className="container">
        <div className="showcase-header">
          <h2 className="section-title">{t.title}</h2>
          <p className="section-subtitle">{t.subtitle}</p>
        </div>

        <div className="photo-grid">
          {photos.map(photo => (
            <div key={photo.id} className="photo-item">
              <div className="photo-content">
                <div className="photo-placeholder">
                  <i className="fas fa-image"></i>
                </div>
                <div className="photo-info">
                  <span className="photo-category">{photo.category}</span>
                  <p className="photo-description">{photo.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default PhotoShowcase