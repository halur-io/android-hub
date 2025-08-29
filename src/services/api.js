// API Service for fetching data from admin panel
const API_BASE = '/admin/api'

export const api = {
  // Fetch site settings
  async getSettings() {
    try {
      const response = await fetch(`${API_BASE}/settings`)
      if (response.ok) {
        return await response.json()
      }
      return null
    } catch (error) {
      console.error('Error fetching settings:', error)
      return null
    }
  },

  // Fetch branches
  async getBranches() {
    try {
      const response = await fetch(`${API_BASE}/branches`)
      if (response.ok) {
        return await response.json()
      }
      return []
    } catch (error) {
      console.error('Error fetching branches:', error)
      return []
    }
  },

  // Fetch gallery photos
  async getGallery() {
    try {
      const response = await fetch(`${API_BASE}/gallery`)
      if (response.ok) {
        return await response.json()
      }
      return []
    } catch (error) {
      console.error('Error fetching gallery:', error)
      return []
    }
  },

  // Fetch menu
  async getMenu() {
    try {
      const response = await fetch(`${API_BASE}/menu`)
      if (response.ok) {
        return await response.json()
      }
      return []
    } catch (error) {
      console.error('Error fetching menu:', error)
      return []
    }
  },

  // Submit contact form
  async submitContact(formData) {
    try {
      const response = await fetch('/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(formData)
      })
      return response.ok
    } catch (error) {
      console.error('Error submitting contact:', error)
      return false
    }
  },

  // Submit reservation
  async submitReservation(formData) {
    try {
      const response = await fetch('/reservation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(formData)
      })
      return response.ok
    } catch (error) {
      console.error('Error submitting reservation:', error)
      return false
    }
  }
}