(function() {
    'use strict';
    
    function trackEvent(eventName, eventData) {
        if (typeof window.dataLayer !== 'undefined') {
            window.dataLayer.push({
                'event': eventName,
                ...eventData
            });
            console.log('[GTM Track]', eventName, eventData);
        }
    }
    
    function initClickTracking() {
        document.addEventListener('click', function(e) {
            var target = e.target.closest('[data-gtm-event]');
            if (!target) return;
            
            var eventName = target.getAttribute('data-gtm-event');
            var eventLabel = target.getAttribute('data-gtm-label') || '';
            var eventCategory = target.getAttribute('data-gtm-category') || 'engagement';
            
            trackEvent(eventName, {
                event_category: eventCategory,
                event_label: eventLabel,
                click_url: target.href || '',
                click_text: target.textContent.trim().substring(0, 50),
                page_location: window.location.href
            });
        });
        
        document.querySelectorAll('a[href^="tel:"]').forEach(function(link) {
            if (!link.hasAttribute('data-gtm-event')) {
                link.setAttribute('data-gtm-event', 'phone_call');
                link.setAttribute('data-gtm-label', link.href.replace('tel:', ''));
                link.setAttribute('data-gtm-category', 'contact');
            }
        });
        
        document.querySelectorAll('a[href*="wa.me"], a[href*="whatsapp"]').forEach(function(link) {
            if (!link.hasAttribute('data-gtm-event')) {
                link.setAttribute('data-gtm-event', 'whatsapp_click');
                link.setAttribute('data-gtm-label', 'WhatsApp');
                link.setAttribute('data-gtm-category', 'contact');
            }
        });
        
        document.querySelectorAll('a[href*="waze.com"], a[href*="maps.google"], a[href*="goo.gl/maps"]').forEach(function(link) {
            if (!link.hasAttribute('data-gtm-event')) {
                link.setAttribute('data-gtm-event', 'get_directions');
                link.setAttribute('data-gtm-label', link.href.includes('waze') ? 'Waze' : 'Google Maps');
                link.setAttribute('data-gtm-category', 'navigation');
            }
        });
        
        document.querySelectorAll('a[href*="reservation"], a[href*="#reservation"], .mobile-nav-item[href*="tabit"], .mobile-nav-item[href*="ontopo"]').forEach(function(link) {
            var text = link.textContent.trim();
            if (text.includes('הזמנ') || text.includes('Reserve') || text.includes('שולחן')) {
                if (!link.hasAttribute('data-gtm-event')) {
                    link.setAttribute('data-gtm-event', 'book_table');
                    link.setAttribute('data-gtm-label', 'Table Reservation');
                    link.setAttribute('data-gtm-category', 'conversion');
                }
            }
        });
        
        document.querySelectorAll('a[href*="/menu"], a[href*="#menu"]').forEach(function(link) {
            if (!link.hasAttribute('data-gtm-event')) {
                link.setAttribute('data-gtm-event', 'view_menu');
                link.setAttribute('data-gtm-label', 'Menu');
                link.setAttribute('data-gtm-category', 'engagement');
            }
        });
        
        document.querySelectorAll('a[href*="/order"], a[href*="#order"]').forEach(function(link) {
            if (!link.hasAttribute('data-gtm-event')) {
                link.setAttribute('data-gtm-event', 'start_order');
                link.setAttribute('data-gtm-label', 'Online Order');
                link.setAttribute('data-gtm-category', 'conversion');
            }
        });
        
        document.querySelectorAll('a[href*="facebook.com"]').forEach(function(link) {
            if (!link.hasAttribute('data-gtm-event')) {
                link.setAttribute('data-gtm-event', 'social_click');
                link.setAttribute('data-gtm-label', 'Facebook');
                link.setAttribute('data-gtm-category', 'social');
            }
        });
        
        document.querySelectorAll('a[href*="instagram.com"]').forEach(function(link) {
            if (!link.hasAttribute('data-gtm-event')) {
                link.setAttribute('data-gtm-event', 'social_click');
                link.setAttribute('data-gtm-label', 'Instagram');
                link.setAttribute('data-gtm-category', 'social');
            }
        });
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initClickTracking);
    } else {
        initClickTracking();
    }
    
    window.gtmTrack = trackEvent;
})();
