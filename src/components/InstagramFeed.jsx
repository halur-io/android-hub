import React from 'react'
import './InstagramFeed.css'

const InstagramFeed = ({ language }) => {
  const translations = {
    he: {
      title: 'עקבו אחרינו באינסטגרם',
      subtitle: '@sumo_asian_kitchen',
      followBtn: 'עקבו אחרינו'
    },
    en: {
      title: 'Follow us on Instagram',
      subtitle: '@sumo_asian_kitchen',
      followBtn: 'Follow Us'
    }
  }

  const t = translations[language]

  // Mock Instagram posts - in real app, these would come from Instagram API
  const posts = [
    { id: 1, type: 'image', alt: 'Sushi Platter' },
    { id: 2, type: 'image', alt: 'Ramen Bowl' },
    { id: 3, type: 'image', alt: 'Thai Curry' },
    { id: 4, type: 'image', alt: 'Spring Rolls' },
    { id: 5, type: 'image', alt: 'Pad Thai' },
    { id: 6, type: 'image', alt: 'Dessert' }
  ]

  return (
    <section className="instagram-feed">
      <div className="container">
        <div className="instagram-header">
          <h2 className="section-title">{t.title}</h2>
          <p className="instagram-handle">{t.subtitle}</p>
        </div>

        <div className="instagram-grid">
          {posts.map(post => (
            <div key={post.id} className="instagram-post">
              <div className="post-placeholder">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                  <circle cx="8.5" cy="8.5" r="1.5"></circle>
                  <polyline points="21 15 16 10 5 21"></polyline>
                </svg>
                <span>{post.alt}</span>
              </div>
              <div className="post-overlay">
                <div className="post-stats">
                  <span>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                    </svg>
                    {Math.floor(Math.random() * 500) + 100}
                  </span>
                  <span>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    {Math.floor(Math.random() * 50) + 10}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="instagram-cta">
          <a 
            href="https://www.instagram.com/sumo_asian_kitchen" 
            target="_blank" 
            rel="noopener noreferrer"
            className="instagram-follow-btn"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
              <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
              <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
            </svg>
            {t.followBtn}
          </a>
        </div>
      </div>
    </section>
  )
}

export default InstagramFeed