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

  // 8 photos for the showcase
  const photos = [
    { id: 1, alt: 'Sushi Selection' },
    { id: 2, alt: 'Restaurant Interior' },
    { id: 3, alt: 'Signature Roll' },
    { id: 4, alt: 'Dining Area' },
    { id: 5, alt: 'Fresh Sashimi' },
    { id: 6, alt: 'Bar Counter' },
    { id: 7, alt: 'Wok Dishes' },
    { id: 8, alt: 'Dessert Selection' }
  ]

  return (
    <section className="photo-showcase">
      <div className="container">
        <div className="photo-grid-2col">
          {photos.map(photo => (
            <div key={photo.id} className="photo-item-simple">
              <div className="photo-placeholder-simple">
                <i className="fas fa-image"></i>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default PhotoShowcase