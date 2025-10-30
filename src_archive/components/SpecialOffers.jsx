import React from 'react'
import './SpecialOffers.css'

const SpecialOffers = ({ language }) => {
  const translations = {
    he: {
      title: 'ימים מיוחדים',
      subtitle: 'הטבות בלעדיות לאורך כל השבוע',
      sunday: 'ראשון',
      tuesday: 'שלישי',
      thursday: 'חמישי',
      sundayOffer: 'הנחה 15%',
      sundayDesc: 'על כל התפריט',
      tuesdayOffer: 'מוקפצים',
      tuesdayDesc: '3 מוקפצים ב-120 ₪',
      thursdayOffer: 'סושי ספיישל',
      thursdayDesc: '1+1 על רולים נבחרים',
      callNow: 'הזמינו עכשיו'
    },
    en: {
      title: 'Special Days',
      subtitle: 'Exclusive offers throughout the week',
      sunday: 'Sunday',
      tuesday: 'Tuesday',
      thursday: 'Thursday',
      sundayOffer: '15% Off',
      sundayDesc: 'On entire menu',
      tuesdayOffer: 'Stir Fry',
      tuesdayDesc: '3 for 120 NIS',
      thursdayOffer: 'Sushi Special',
      thursdayDesc: '1+1 on selected rolls',
      callNow: 'Order Now'
    }
  }

  const t = translations[language]

  const offers = [
    {
      day: t.sunday,
      offer: t.sundayOffer,
      description: t.sundayDesc,
      icon: '🍜',
      color: '#FF6B6B'
    },
    {
      day: t.tuesday,
      offer: t.tuesdayOffer,
      description: t.tuesdayDesc,
      icon: '🥘',
      color: '#4ECDC4'
    },
    {
      day: t.thursday,
      offer: t.thursdayOffer,
      description: t.thursdayDesc,
      icon: '🍣',
      color: '#FFD93D'
    }
  ]

  return (
    <section className="special-offers">
      <div className="container">
        <h2 className="section-title">{t.title}</h2>
        <p className="section-subtitle">{t.subtitle}</p>

        <div className="offers-grid">
          {offers.map((offer, index) => (
            <div key={index} className="offer-card" style={{'--accent-color': offer.color}}>
              <div className="offer-icon">{offer.icon}</div>
              <div className="offer-day">{offer.day}</div>
              <h3 className="offer-title">{offer.offer}</h3>
              <p className="offer-description">{offer.description}</p>
              <a href="tel:077-806-6300" className="offer-cta">
                {t.callNow}
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default SpecialOffers