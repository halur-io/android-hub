// Main JavaScript functionality for Sumo Restaurant Website

document.addEventListener('DOMContentLoaded', function() {
    // Navbar scroll effect
    initNavbarScroll();
    
    // Smooth scrolling for navigation links
    initSmoothScrolling();
    
    // Form validations
    initFormValidations();
    
    // Gallery lightbox effect
    initGalleryEffects();
    
    // Auto-hide flash messages
    initFlashMessages();
    
    // Mobile menu handling
    initMobileMenu();
});

/**
 * Initialize navbar scroll effects
 */
function initNavbarScroll() {
    const navbar = document.getElementById('mainNav');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });
}

/**
 * Initialize smooth scrolling for navigation links
 */
function initSmoothScrolling() {
    const navLinks = document.querySelectorAll('.nav-link[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const navbarHeight = document.querySelector('.navbar').offsetHeight;
                const targetPosition = targetElement.offsetTop - navbarHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse.classList.contains('show')) {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                    bsCollapse.hide();
                }
            }
        });
    });
}

/**
 * Initialize form validations
 */
function initFormValidations() {
    // Contact form validation
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            if (!validateContactForm()) {
                e.preventDefault();
            }
        });
    }
    
    // Reservation form validation
    const reservationForm = document.querySelector('.reservation-form');
    if (reservationForm) {
        reservationForm.addEventListener('submit', function(e) {
            if (!validateReservationForm()) {
                e.preventDefault();
            }
        });
    }
    
    // Real-time validation
    addRealTimeValidation();
}

/**
 * Validate contact form
 */
function validateContactForm() {
    const form = document.querySelector('.contact-form');
    const name = form.querySelector('input[name="name"]');
    const email = form.querySelector('input[name="email"]');
    const phone = form.querySelector('input[name="phone"]');
    const message = form.querySelector('textarea[name="message"]');
    
    let isValid = true;
    
    // Name validation
    if (!name.value.trim() || name.value.length < 2) {
        showFieldError(name, 'אנא הזן שם תקין (לפחות 2 תווים)');
        isValid = false;
    } else {
        clearFieldError(name);
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.value)) {
        showFieldError(email, 'אנא הזן כתובת אימייל תקינה');
        isValid = false;
    } else {
        clearFieldError(email);
    }
    
    // Phone validation
    const phoneRegex = /^[\d-+\s()]{9,15}$/;
    if (!phoneRegex.test(phone.value)) {
        showFieldError(phone, 'אנא הזן מספר טלפון תקין');
        isValid = false;
    } else {
        clearFieldError(phone);
    }
    
    // Message validation
    if (!message.value.trim() || message.value.length < 10) {
        showFieldError(message, 'אנא הזן הודעה (לפחות 10 תווים)');
        isValid = false;
    } else {
        clearFieldError(message);
    }
    
    return isValid;
}

/**
 * Validate reservation form
 */
function validateReservationForm() {
    const form = document.querySelector('.reservation-form');
    const name = form.querySelector('input[name="name"]');
    const email = form.querySelector('input[name="email"]');
    const phone = form.querySelector('input[name="phone"]');
    const date = form.querySelector('input[name="date"]');
    const time = form.querySelector('input[name="time"]');
    
    let isValid = true;
    
    // Name validation
    if (!name.value.trim() || name.value.length < 2) {
        showFieldError(name, 'אנא הזן שם תקין');
        isValid = false;
    } else {
        clearFieldError(name);
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.value)) {
        showFieldError(email, 'אנא הזן כתובת אימייל תקינה');
        isValid = false;
    } else {
        clearFieldError(email);
    }
    
    // Phone validation
    const phoneRegex = /^[\d-+\s()]{9,15}$/;
    if (!phoneRegex.test(phone.value)) {
        showFieldError(phone, 'אנא הזן מספר טלפון תקין');
        isValid = false;
    } else {
        clearFieldError(phone);
    }
    
    // Date validation
    const selectedDate = new Date(date.value);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    if (!date.value || selectedDate < today) {
        showFieldError(date, 'אנא בחר תאריך תקין (היום או בעתיד)');
        isValid = false;
    } else {
        clearFieldError(date);
    }
    
    // Time validation
    if (!time.value) {
        showFieldError(time, 'אנא בחר שעה');
        isValid = false;
    } else {
        clearFieldError(time);
    }
    
    return isValid;
}

/**
 * Add real-time validation to form fields
 */
function addRealTimeValidation() {
    const inputs = document.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.hasAttribute('required') || this.value.trim()) {
                validateField(this);
            }
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });
}

/**
 * Validate individual field
 */
function validateField(field) {
    const fieldName = field.getAttribute('name');
    const value = field.value.trim();
    
    switch (fieldName) {
        case 'name':
            if (value.length < 2) {
                showFieldError(field, 'שם חייב להכיל לפחות 2 תווים');
                return false;
            }
            break;
            
        case 'email':
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                showFieldError(field, 'כתובת אימייל לא תקינה');
                return false;
            }
            break;
            
        case 'phone':
            const phoneRegex = /^[\d-+\s()]{9,15}$/;
            if (!phoneRegex.test(value)) {
                showFieldError(field, 'מספר טלפון לא תקין');
                return false;
            }
            break;
            
        case 'message':
            if (value.length < 10) {
                showFieldError(field, 'הודעה חייבת להכיל לפחות 10 תווים');
                return false;
            }
            break;
    }
    
    clearFieldError(field);
    return true;
}

/**
 * Show field error
 */
function showFieldError(field, message) {
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');
    
    // Remove existing error message
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
    
    // Add new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

/**
 * Clear field error
 */
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
    
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

/**
 * Initialize gallery effects
 */
function initGalleryEffects() {
    const galleryItems = document.querySelectorAll('.gallery-item');
    
    galleryItems.forEach(item => {
        const img = item.querySelector('img');
        if (img) {
            item.addEventListener('click', function() {
                createLightbox(img.src, img.alt);
            });
        }
    });
}

/**
 * Create lightbox for gallery images
 */
function createLightbox(src, alt) {
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
        <div class="lightbox-content">
            <span class="lightbox-close">&times;</span>
            <img src="${src}" alt="${alt}">
        </div>
    `;
    
    // Add styles
    lightbox.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        cursor: pointer;
    `;
    
    const content = lightbox.querySelector('.lightbox-content');
    content.style.cssText = `
        position: relative;
        max-width: 90%;
        max-height: 90%;
    `;
    
    const img = lightbox.querySelector('img');
    img.style.cssText = `
        width: 100%;
        height: auto;
        max-height: 90vh;
        object-fit: contain;
    `;
    
    const closeBtn = lightbox.querySelector('.lightbox-close');
    closeBtn.style.cssText = `
        position: absolute;
        top: -40px;
        right: 0;
        color: white;
        font-size: 30px;
        font-weight: bold;
        cursor: pointer;
        z-index: 10000;
    `;
    
    document.body.appendChild(lightbox);
    
    // Close lightbox events
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) {
            document.body.removeChild(lightbox);
        }
    });
    
    closeBtn.addEventListener('click', function() {
        document.body.removeChild(lightbox);
    });
    
    // ESC key to close
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && document.body.contains(lightbox)) {
            document.body.removeChild(lightbox);
        }
    });
}

/**
 * Initialize flash messages auto-hide
 */
function initFlashMessages() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-20px)';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, 300);
            }
        }, 5000);
    });
}

/**
 * Initialize mobile menu handling
 */
function initMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            // Add animation class
            navbarCollapse.classList.toggle('show');
        });
    }
}

/**
 * Animate elements on scroll
 */
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);
    
    // Observe elements
    const elementsToAnimate = document.querySelectorAll('.menu-category, .gallery-item, .contact-item');
    elementsToAnimate.forEach(el => observer.observe(el));
}

// Initialize scroll animations after DOM is loaded
document.addEventListener('DOMContentLoaded', initScrollAnimations);

/**
 * Form submission loading states
 */
function initFormSubmissionStates() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.setAttribute('data-original-text', submitBtn.innerHTML);
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> שולח...';
                
                // Re-enable after 3 seconds as fallback
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'שליחה';
                }, 3000);
            }
        });
    });
}

// Initialize form submission states
document.addEventListener('DOMContentLoaded', initFormSubmissionStates);
