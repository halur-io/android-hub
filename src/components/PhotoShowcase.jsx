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
    { id: 1, src: '/static/images/photo1.jpg', alt: 'Sumo Restaurant' },
    { id: 2, src: '/static/images/photo2.jpg', alt: 'Asian Cuisine' },
    { id: 3, src: '/static/images/photo3.jpg', alt: 'Restaurant Dish' },
    { id: 4, src: '/static/images/photo4.png', alt: 'Sumo Logo' },
    { id: 5, src: '/static/images/photo5.png', alt: 'Elegant Sushi Platter' },
    { id: 6, src: '/static/images/photo6.png', alt: 'Restaurant Interior' },
    { id: 7, src: '/static/images/photo7.png', alt: 'Ramen Bowl' },
    { id: 8, src: '/static/images/photo8.png', alt: 'Wok Cooking' }
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