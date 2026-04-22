import React, { useState, useEffect } from 'react'
import './PhotoShowcase.css'
import { api } from '../services/api'

const PhotoShowcase = ({ language }) => {
  const [gallery, setGallery] = useState([])
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

  useEffect(() => {
    api.getGallery().then(data => {
      if (data && data.length > 0) setGallery(data)
    })
  }, [])

  // Default photos if no gallery from admin
  const defaultPhotos = [
    { id: 1, file_path: '/static/images/photo5.png', caption_he: 'מגש סושי מרהיב', caption_en: 'Elegant Sushi Platter' },
    { id: 2, file_path: '/static/images/photo6.png', caption_he: 'פנים המסעדה', caption_en: 'Restaurant Interior' },
    { id: 3, file_path: '/static/images/photo7.png', caption_he: 'קערת ראמן', caption_en: 'Ramen Bowl' },
    { id: 4, file_path: '/static/images/photo8.png', caption_he: 'בישול בווק', caption_en: 'Wok Cooking' },
    { id: 5, file_path: '/static/images/photo9.png', caption_he: 'דרגון רול סושי', caption_en: 'Dragon Roll Sushi' },
    { id: 6, file_path: '/static/images/photo10.png', caption_he: 'בר המסעדה', caption_en: 'Restaurant Bar' },
    { id: 7, file_path: '/static/images/photo11.png', caption_he: 'מגש סשימי', caption_en: 'Sashimi Platter' },
    { id: 8, file_path: '/static/images/photo12.png', caption_he: 'מגש מנות ראשונות', caption_en: 'Appetizer Platter' }
  ]

  const photos = gallery.length > 0 ? gallery : defaultPhotos

  return (
    <section className="photo-showcase">
      <div className="photo-container">
        <div className="photo-grid-2col">
          {photos.map(photo => (
            <div key={photo.id} className="photo-item-simple">
              <img 
                src={photo.file_path} 
                alt={language === 'he' ? photo.caption_he : photo.caption_en} 
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