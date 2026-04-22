import React from 'react'
import './Gallery.css'

const Gallery = ({ language }) => {
  const translations = {
    he: {
      title: 'גלריה',
      subtitle: 'צפו במנות המדהימות שלנו'
    },
    en: {
      title: 'Gallery',
      subtitle: 'View our amazing dishes'
    }
  }

  const t = translations[language]

  const galleryImages = [
    { 
      id: 1, 
      alt: 'Premium Sushi Selection',
      category: 'סושי',
      description: 'Fresh premium sushi rolls'
    },
    { 
      id: 2, 
      alt: 'Special Roll Combo',
      category: 'קומבינציות',
      description: 'Chef special combination'
    },
    { 
      id: 3, 
      alt: 'Wok Noodles',
      category: 'ווק',
      description: 'Stir-fried noodles with vegetables'
    },
    { 
      id: 4, 
      alt: 'Tempura Platter',
      category: 'טמפורה',
      description: 'Crispy tempura selection'
    },
    { 
      id: 5, 
      alt: 'Pad Thai',
      category: 'תאילנדי',
      description: 'Classic Thai noodles'
    },
    { 
      id: 6, 
      alt: 'Salmon Teriyaki',
      category: 'דגים',
      description: 'Grilled salmon with teriyaki'
    },
    { 
      id: 7, 
      alt: 'Ramen Bowl',
      category: 'ראמן',
      description: 'Traditional Japanese ramen'
    },
    { 
      id: 8, 
      alt: 'Asian Desserts',
      category: 'קינוחים',
      description: 'Sweet treats selection'
    }
  ]

  return (
    <section id="gallery" className="gallery-section">
      <div className="container">
        <h2 className="section-title">{t.title}</h2>
        <p className="section-subtitle">{t.subtitle}</p>

        <div className="gallery-grid">
          {galleryImages.map(image => (
            <div key={image.id} className="gallery-item">
              <div className="gallery-image-wrapper">
                <div className="gallery-image-placeholder">
                  <i className="fas fa-utensils"></i>
                </div>
                <div className="gallery-overlay">
                  <span className="gallery-category">{image.category}</span>
                  <h4 className="gallery-title">{image.alt}</h4>
                  <p className="gallery-description">{image.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Gallery