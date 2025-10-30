import React from 'react'
import './BranchModal.css'

const BranchModal = ({ isOpen, onClose, actionType, language }) => {
  if (!isOpen) return null

  const translations = {
    he: {
      title: 'בחר סניף',
      rama: 'ראמה',
      karmiel: 'כרמיאל',
      ramaAddress: 'כפר ראמה, רחוב ראשי',
      karmielAddress: 'כרמיאל, מרכז העיר',
      ramaPhone: '077-806-6300',
      karmielPhone: '077-806-6301',
      close: 'סגור',
      takeaway: 'הזמנה טלפונית',
      delivery: 'משלוח WhatsApp',
      reservations: 'הזמנת שולחן'
    },
    en: {
      title: 'Choose Branch',
      rama: 'Rama',
      karmiel: 'Karmiel',
      ramaAddress: 'Rama Village, Main Street',
      karmielAddress: 'Karmiel, City Center',
      ramaPhone: '077-806-6300',
      karmielPhone: '077-806-6301',
      close: 'Close',
      takeaway: 'Phone Order',
      delivery: 'WhatsApp Delivery',
      reservations: 'Table Reservation'
    }
  }

  const t = translations[language]

  const handleBranchAction = (branch) => {
    const phone = branch === 'rama' ? t.ramaPhone : t.karmielPhone
    
    switch(actionType) {
      case 'takeaway':
        window.location.href = `tel:${phone.replace(/-/g, '')}`
        break
      case 'delivery':
        const whatsappNumber = phone.replace(/-/g, '').replace('077', '97277')
        window.open(`https://wa.me/${whatsappNumber}`, '_blank')
        break
      case 'reservations':
        // Scroll to contact form
        const contactSection = document.getElementById('contact')
        if (contactSection) {
          contactSection.scrollIntoView({ behavior: 'smooth' })
        }
        onClose()
        break
      default:
        break
    }
  }

  const getActionTitle = () => {
    switch(actionType) {
      case 'takeaway': return t.takeaway
      case 'delivery': return t.delivery
      case 'reservations': return t.reservations
      default: return ''
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          <i className="fas fa-times"></i>
        </button>
        
        <div className="modal-header">
          <h2>{t.title}</h2>
          <p className="modal-action-type">{getActionTitle()}</p>
        </div>

        <div className="branches-selection">
          <div 
            className="branch-option" 
            onClick={() => handleBranchAction('rama')}
          >
            <div className="branch-option-header">
              <i className="fas fa-map-marker-alt"></i>
              <h3>{t.rama}</h3>
            </div>
            <div className="branch-option-details">
              <p className="branch-address">{t.ramaAddress}</p>
              <p className="branch-phone">
                <i className="fas fa-phone"></i>
                {t.ramaPhone}
              </p>
            </div>
            <div className="branch-option-arrow">
              <i className="fas fa-chevron-right"></i>
            </div>
          </div>

          <div 
            className="branch-option" 
            onClick={() => handleBranchAction('karmiel')}
          >
            <div className="branch-option-header">
              <i className="fas fa-map-marker-alt"></i>
              <h3>{t.karmiel}</h3>
            </div>
            <div className="branch-option-details">
              <p className="branch-address">{t.karmielAddress}</p>
              <p className="branch-phone">
                <i className="fas fa-phone"></i>
                {t.karmielPhone}
              </p>
            </div>
            <div className="branch-option-arrow">
              <i className="fas fa-chevron-right"></i>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default BranchModal