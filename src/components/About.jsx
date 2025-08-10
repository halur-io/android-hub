import React from 'react'
import './About.css'

const About = ({ language }) => {
  const translations = {
    he: {
      title: 'סיפור סומו',
      subtitle: 'שני סניפים, חוויה אחת בלתי נשכחת',
      intro: 'המסע האסייתי שלכם מתחיל כאן',
      description1: 'סומו היא יותר ממסעדה - היא חוויה קולינרית שמשלבת את המיטב של המטבח האסייתי עם נגיעות מודרניות. משנת הקמתנו, אנו מחויבים להגיש את האוכל האסייתי האיכותי ביותר בצפון.',
      description2: 'עם שני סניפים בראמה וכרמיאל, אנו מביאים את הטעמים האותנטיים של אסיה קרוב לבית שלכם.',
      whyTitle: 'למה סומו?',
      freshIngredients: 'חומרי גלם טריים',
      freshDesc: 'אנו עובדים רק עם הספקים הטובים ביותר',
      expertChefs: 'שפים מומחים',
      chefDesc: 'צוות מקצועי עם שנים של ניסיון',
      uniqueAtmosphere: 'אווירה ייחודית',
      atmosphereDesc: 'עיצוב מודרני ואווירה נעימה',
      branchesTitle: 'הסניפים שלנו',
      ramaTitle: 'סומו ראמה',
      ramaDesc: 'הסניף הראשון שלנו, לב הקהילה המקומית',
      ramaAddress: 'כפר ראמה, רחוב ראשי',
      karmielTitle: 'סומו כרמיאל',
      karmielDesc: 'חוויה עירונית עם טאץ\' מקומי',
      karmielAddress: 'כרמיאל, מרכז העיר',
      phone: 'טלפון'
    },
    en: {
      title: 'The SUMO Story',
      subtitle: 'Two Branches, One Unforgettable Experience',
      intro: 'Your Asian journey starts here',
      description1: 'SUMO is more than a restaurant - it\'s a culinary experience that combines the best of Asian cuisine with modern touches. Since our establishment, we are committed to serving the highest quality Asian food in the North.',
      description2: 'With two branches in Rama and Karmiel, we bring the authentic flavors of Asia close to your home.',
      whyTitle: 'Why SUMO?',
      freshIngredients: 'Fresh Ingredients',
      freshDesc: 'We work only with the best suppliers',
      expertChefs: 'Expert Chefs',
      chefDesc: 'Professional team with years of experience',
      uniqueAtmosphere: 'Unique Atmosphere',
      atmosphereDesc: 'Modern design and pleasant ambiance',
      branchesTitle: 'Our Branches',
      ramaTitle: 'SUMO Rama',
      ramaDesc: 'Our first branch, heart of the local community',
      ramaAddress: 'Rama Village, Main Street',
      karmielTitle: 'SUMO Karmiel',
      karmielDesc: 'Urban experience with a local touch',
      karmielAddress: 'Karmiel, City Center',
      phone: 'Phone'
    }
  }

  const t = translations[language]

  return (
    <section id="about" className="about-section">
      <div className="container">
        <div className="about-header">
          <h2 className="section-title">{t.title}</h2>
          <p className="section-subtitle">{t.subtitle}</p>
          <div className="intro-line">{t.intro}</div>
        </div>
        
        <div className="about-content">
          <div className="about-story">
            <p className="story-text">{t.description1}</p>
            <p className="story-text highlight">{t.description2}</p>
          </div>

          <div className="why-section">
            <h3 className="why-title">{t.whyTitle}</h3>
            <div className="features-grid">
              <div className="feature-card">
                <div className="feature-icon">
                  <i className="fas fa-leaf"></i>
                </div>
                <h4>{t.freshIngredients}</h4>
                <p>{t.freshDesc}</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">
                  <i className="fas fa-user-tie"></i>
                </div>
                <h4>{t.expertChefs}</h4>
                <p>{t.chefDesc}</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">
                  <i className="fas fa-star"></i>
                </div>
                <h4>{t.uniqueAtmosphere}</h4>
                <p>{t.atmosphereDesc}</p>
              </div>
            </div>
          </div>

          <div className="branches-section">
            <h3 className="branches-title">{t.branchesTitle}</h3>
            <div className="branches-grid">
              <div className="branch-card rama-branch">
                <div className="branch-card-inner">
                  <div className="branch-icon">
                    <i className="fas fa-map-marker-alt"></i>
                  </div>
                  <h4>{t.ramaTitle}</h4>
                  <p className="branch-desc">{t.ramaDesc}</p>
                  <div className="branch-info">
                    <p className="branch-address">
                      <i className="fas fa-location-dot"></i>
                      {t.ramaAddress}
                    </p>
                    <p className="branch-phone">
                      <i className="fas fa-phone"></i>
                      077-806-6300
                    </p>
                  </div>
                </div>
              </div>

              <div className="branch-card karmiel-branch">
                <div className="branch-card-inner">
                  <div className="branch-icon">
                    <i className="fas fa-map-marker-alt"></i>
                  </div>
                  <h4>{t.karmielTitle}</h4>
                  <p className="branch-desc">{t.karmielDesc}</p>
                  <div className="branch-info">
                    <p className="branch-address">
                      <i className="fas fa-location-dot"></i>
                      {t.karmielAddress}
                    </p>
                    <p className="branch-phone">
                      <i className="fas fa-phone"></i>
                      077-806-6301
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default About