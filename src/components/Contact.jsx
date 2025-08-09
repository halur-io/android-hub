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
      title: 'הסניפים שלנו',
      subtitle: 'בקרו אותנו באחד משני הסניפים',
      branchesTitle: 'הסניפים שלנו',
      ramaTitle: 'סניף ראמה',
      carmielTitle: 'סניף כרמיאל',
      reservationTitle: 'להזמנת שולחן',
      reservationSubtitle: 'צרו איתנו קשר טלפוני או בוואטסאפ',
      callNow: 'חייגו עכשיו',
      sendWhatsapp: 'שלחו וואטסאפ',
      name: 'שם מלא',
      email: 'אימייל',
      phone: 'טלפון',
      message: 'הודעה',
      sendBtn: 'שלח הודעה',
      ramaAddress: 'ראמה, הכפר',
      carmielAddress: 'כרמיאל, מרכז העיר',
      hours: 'ראשון-חמישי: 12:00-23:00\nשישי-שבת: 12:00-01:00',
      contactFormTitle: 'שלחו לנו הודעה'
    },
    en: {
      title: 'Our Branches',
      subtitle: 'Visit us at one of our two locations',
      branchesTitle: 'Our Branches',
      ramaTitle: 'Rama Branch',
      carmielTitle: 'Carmiel Branch',
      reservationTitle: 'Table Reservation',
      reservationSubtitle: 'Contact us by phone or WhatsApp',
      callNow: 'Call Now',
      sendWhatsapp: 'Send WhatsApp',
      name: 'Full Name',
      email: 'Email',
      phone: 'Phone',
      message: 'Message',
      sendBtn: 'Send Message',
      ramaAddress: 'Rama Village',
      carmielAddress: 'Carmiel City Center',
      hours: 'Sun-Thu: 12:00-23:00\nFri-Sat: 12:00-01:00',
      contactFormTitle: 'Send us a message'
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

        {/* Branches Section */}
        <div className="branches-container">
          <div className="branch-card">
            <div className="branch-header">
              <i className="fas fa-store"></i>
              <h3>{t.ramaTitle}</h3>
            </div>
            <div className="branch-info">
              <div className="info-item">
                <i className="fas fa-map-marker-alt"></i>
                <p>{t.ramaAddress}</p>
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
          </div>

          <div className="branch-card">
            <div className="branch-header">
              <i className="fas fa-store"></i>
              <h3>{t.carmielTitle}</h3>
            </div>
            <div className="branch-info">
              <div className="info-item">
                <i className="fas fa-map-marker-alt"></i>
                <p>{t.carmielAddress}</p>
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
          </div>
        </div>

        {/* Reservation Call to Action */}
        <div id="reservations" className="reservation-cta">
          <h3>{t.reservationTitle}</h3>
          <p>{t.reservationSubtitle}</p>
          <div className="cta-buttons">
            <a href="tel:077-806-6300" className="cta-btn call-btn">
              <i className="fas fa-phone"></i>
              <span>{t.callNow}</span>
            </a>
            <a href="https://wa.me/972778066300?text=שלום, אני רוצה להזמין שולחן" className="cta-btn whatsapp-btn">
              <i className="fab fa-whatsapp"></i>
              <span>{t.sendWhatsapp}</span>
            </a>
          </div>
        </div>

        {/* Contact Form */}
        <div className="contact-form-section">
          <h3>{t.contactFormTitle}</h3>
          <form className="contact-form" onSubmit={handleSubmit}>
            <div className="form-grid">
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
            </div>
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
      </div>
    </section>
  )
}

export default Contact