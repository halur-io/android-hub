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
      {/* Interactive particles */}
      <div className="about-particles">
        <span className="particle-about"></span>
        <span className="particle-about"></span>
        <span className="particle-about"></span>
        <span className="particle-about"></span>
        <span className="particle-about"></span>
      </div>
      
      <div className="container">
        <div className="about-header">
          <h2 className="section-title">{t.title}</h2>
          <p className="section-subtitle">{t.subtitle}</p>
        </div>
        
        <div className="about-content">
          <div className="about-story">
            <p className="story-text main">{t.description1}</p>
          </div>
        </div>
      </div>
    </section>
  )
}

export default About