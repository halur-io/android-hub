// SushiFushi Inspired JavaScript
document.addEventListener('DOMContentLoaded', function() {
    
    // Smooth scrolling for navigation links
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const offsetTop = targetSection.offsetTop - 80;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    let lastScroll = 0;
    
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        lastScroll = currentScroll;
    });
    
    // Menu tabs functionality
    const menuTabs = document.querySelectorAll('.menu-tab');
    const menuCategories = document.querySelectorAll('.menu-category-items');
    
    menuTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const category = this.dataset.category;
            
            // Update active tab
            menuTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Show/hide menu items
            menuCategories.forEach(cat => {
                if (cat.dataset.category === category) {
                    cat.style.display = 'grid';
                    cat.style.gridTemplateColumns = 'repeat(auto-fit, minmax(350px, 1fr))';
                    cat.style.gap = '3rem';
                    cat.style.maxWidth = '1200px';
                    cat.style.margin = '0 auto';
                    
                    // Animate items
                    const items = cat.querySelectorAll('.menu-item');
                    items.forEach((item, index) => {
                        item.style.opacity = '0';
                        item.style.transform = 'translateY(20px)';
                        setTimeout(() => {
                            item.style.transition = 'all 0.5s ease';
                            item.style.opacity = '1';
                            item.style.transform = 'translateY(0)';
                        }, index * 100);
                    });
                } else {
                    cat.style.display = 'none';
                }
            });
        });
    });
    
    // Initialize first category
    const firstCategory = document.querySelector('.menu-category-items[data-category="starters"]');
    if (firstCategory) {
        firstCategory.style.display = 'grid';
        firstCategory.style.gridTemplateColumns = 'repeat(auto-fit, minmax(350px, 1fr))';
        firstCategory.style.gap = '3rem';
        firstCategory.style.maxWidth = '1200px';
        firstCategory.style.margin = '0 auto';
    }
    
    // Fade in animation on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach(el => observer.observe(el));
    
    // Auto-hide flash messages
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'slideOutRight 0.5s forwards';
            setTimeout(() => {
                message.remove();
            }, 500);
        }, 5000);
    });
    
    // Add parallax effect to hero
    const hero = document.querySelector('.hero-background');
    if (hero) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const parallax = scrolled * 0.5;
            hero.style.transform = `translateY(${parallax}px)`;
        });
    }
    
    // Menu item hover effect
    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(10px)';
        });
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
        });
    });
    
});

// Add animation for slideOutRight
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);