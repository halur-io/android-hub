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
    { id: 1, src: '/static/images/photo1.jpg', alt: 'Sushi Selection' },
    { id: 2, src: '/static/images/photo2.jpg', alt: 'Restaurant Interior' },
    { id: 3, src: '/static/images/photo3.jpg', alt: 'Signature Roll' },
    { id: 4, src: '/static/images/photo4.png', alt: 'Dining Area' },
    { id: 5, src: '/static/images/photo5.jpg', alt: 'Fresh Sashimi' },
    { id: 6, src: '/static/images/photo6.jpg', alt: 'Bar Counter' },
    { id: 7, src: '/static/images/photo7.jpg', alt: 'Wok Dishes' },
    { id: 8, src: '/static/images/photo8.png', alt: 'Dessert Selection' }
  ]

  return (
    <section className="photo-showcase">
      <div className="container">
        <div className="photo-grid-2col">
          {photos.map(photo => (
            <div key={photo.id} className="photo-item-simple">
              <img 
                src={photo.src} 
                alt={photo.alt} 
                className="photo-image"
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default PhotoShowcase