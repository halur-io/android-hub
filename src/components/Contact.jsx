import React, { useState } from 'react'
import './Contact.css'

const Contact = ({ language }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    message: ''
  })

  const translations = {
    he: {
      title: 'צור קשר',
      subtitle: 'נשמח לשמוע מכם',
      reservationTitle: 'הזמנת מקום',
      name: 'שם מלא',
      email: 'אימייל',
      phone: 'טלפון',
      message: 'הודעה',
      date: 'תאריך',
      time: 'שעה',
      guests: 'מספר אורחים',
      sendBtn: 'שלח',
      reserveBtn: 'שריין מקום',
      address: 'גולדה מאיר 6, חולון',
      hours: 'ראשון-חמישי: 12:00-23:00\nשישי-שבת: 12:00-01:00'
    },
    en: {
      title: 'Contact Us',
      subtitle: 'We\'d love to hear from you',
      reservationTitle: 'Make a Reservation',
      name: 'Full Name',
      email: 'Email',
      phone: 'Phone',
      message: 'Message',
      date: 'Date',
      time: 'Time',
      guests: 'Number of Guests',
      sendBtn: 'Send',
      reserveBtn: 'Reserve',
      address: '6 Golda Meir, Holon',
      hours: 'Sun-Thu: 12:00-23:00\nFri-Sat: 12:00-01:00'
    }
  }

  const t = translations[language]

  const handleSubmit = (e) => {
    e.preventDefault()
    // Handle form submission
    console.log('Form submitted:', formData)
  }

  return (
    <section id="contact" className="contact-section">
      <div className="container">
        <h2 className="section-title">{t.title}</h2>
        <p className="section-subtitle">{t.subtitle}</p>

        <div className="contact-content">
          <div className="contact-info">
            <div className="info-item">
              <i className="fas fa-map-marker-alt"></i>
              <p>{t.address}</p>
            </div>
            <div className="info-item">
              <i className="fas fa-phone"></i>
              <p>077-806-6300</p>
            </div>
            <div className="info-item">
              <i className="fas fa-clock"></i>
              <p style={{ whiteSpace: 'pre-line' }}>{t.hours}</p>
            </div>
          </div>

          <form className="contact-form" onSubmit={handleSubmit}>
            <input
              type="text"
              placeholder={t.name}
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              required
            />
            <input
              type="email"
              placeholder={t.email}
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              required
            />
            <input
              type="tel"
              placeholder={t.phone}
              value={formData.phone}
              onChange={(e) => setFormData({...formData, phone: e.target.value})}
              required
            />
            <textarea
              placeholder={t.message}
              rows="5"
              value={formData.message}
              onChange={(e) => setFormData({...formData, message: e.target.value})}
              required
            ></textarea>
            <button type="submit" className="btn btn-primary">
              {t.sendBtn}
            </button>
          </form>
        </div>

        <div id="reservations" className="reservation-section">
          <h3 className="reservation-title">{t.reservationTitle}</h3>
          <form className="reservation-form" onSubmit={handleSubmit}>
            <div className="form-row">
              <input type="text" placeholder={t.name} required />
              <input type="tel" placeholder={t.phone} required />
            </div>
            <div className="form-row">
              <input type="date" placeholder={t.date} required />
              <input type="time" placeholder={t.time} required />
            </div>
            <div className="form-row">
              <input type="number" placeholder={t.guests} min="1" max="20" required />
              <button type="submit" className="btn btn-primary">
                {t.reserveBtn}
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>
  )
}

export default Contact