import React from 'react'
import './About.css'

const About = ({ language }) => {
  const translations = {
    he: {
      title: 'אודות סומו',
      subtitle: 'מסעדה אסייתית אותנטית',
      description1: 'ברוכים הבאים לסומו - המקום בו מסורת אסייתית פוגשת חדשנות קולינרית. אנו גאים להגיש לכם את המיטב של המטבח האסייתי, מסושי טרי ועד מנות תאילנדיות חריפות.',
      description2: 'הצוות המקצועי שלנו, בהובלת שפים מנוסים, מכין כל מנה בקפידה ובאהבה, תוך שימוש בחומרי הגלם האיכותיים ביותר.'
    },
    en: {
      title: 'About SUMO',
      subtitle: 'Authentic Asian Restaurant',
      description1: 'Welcome to SUMO - where Asian tradition meets culinary innovation. We are proud to serve you the best of Asian cuisine, from fresh sushi to spicy Thai dishes.',
      description2: 'Our professional team, led by experienced chefs, prepares each dish with care and love, using only the highest quality ingredients.'
    }
  }

  const t = translations[language]

  return (
    <section id="about" className="about-section">
      <div className="container">
        <h2 className="section-title">{t.title}</h2>
        <p className="section-subtitle">{t.subtitle}</p>
        
        <div className="about-content">
          <div className="about-text">
            <p>{t.description1}</p>
            <p>{t.description2}</p>
          </div>
        </div>
      </div>
    </section>
  )
}

export default About