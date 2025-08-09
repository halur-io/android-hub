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
    { id: 1, alt: 'Sushi Platter' },
    { id: 2, alt: 'Ramen Bowl' },
    { id: 3, alt: 'Thai Curry' },
    { id: 4, alt: 'Korean BBQ' },
    { id: 5, alt: 'Vietnamese Pho' },
    { id: 6, alt: 'Desserts' }
  ]

  return (
    <section id="gallery" className="gallery-section">
      <div className="container">
        <h2 className="section-title">{t.title}</h2>
        <p className="section-subtitle">{t.subtitle}</p>

        <div className="gallery-grid">
          {galleryImages.map(image => (
            <div key={image.id} className="gallery-item">
              <div className="gallery-image-placeholder">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                  <circle cx="8.5" cy="8.5" r="1.5"></circle>
                  <polyline points="21 15 16 10 5 21"></polyline>
                </svg>
                <span>{image.alt}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Gallery