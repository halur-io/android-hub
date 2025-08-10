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

  // 8 photos for the showcase - mix of your photos and AI generated
  const photos = [
    { id: 1, src: '/static/images/photo5.png', alt: 'Elegant Sushi Platter' },
    { id: 2, src: '/static/images/photo6.png', alt: 'Restaurant Interior' },
    { id: 3, src: '/static/images/photo7.png', alt: 'Ramen Bowl' },
    { id: 4, src: '/static/images/photo8.png', alt: 'Wok Cooking' },
    { id: 5, src: '/static/images/photo9.png', alt: 'Dragon Roll Sushi' },
    { id: 6, src: '/static/images/photo10.png', alt: 'Restaurant Bar' },
    { id: 7, src: '/static/images/photo11.png', alt: 'Sashimi Platter' },
    { id: 8, src: '/static/images/photo12.png', alt: 'Appetizer Platter' }
  ]

  return (
    <section className="photo-showcase">
      <div className="photo-container">
        <div className="photo-grid-2col">
          {photos.map(photo => (
            <div key={photo.id} className="photo-item-simple">
              <img 
                src={photo.src} 
                alt={photo.alt} 
                className="photo-image"
                onError={(e) => {
                  e.target.style.background = 'rgba(50, 50, 50, 0.5)';
                  e.target.style.minHeight = '200px';
                }}
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default PhotoShowcase