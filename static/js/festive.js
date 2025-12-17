/**
 * Festive Holiday Animations - Christmas & Hanukkah
 * Active from December 2024 until January 15, 2026
 */

(function() {
    'use strict';
    
    // Check if we should show festive animations
    function shouldShowFestive() {
        const now = new Date();
        const endDate = new Date('2026-01-16T00:00:00');
        
        // Disable after January 15, 2026
        if (now >= endDate) {
            return false;
        }
        
        // Check if user prefers reduced motion
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            return false;
        }
        
        // Check localStorage for user preference to disable
        if (localStorage.getItem('festiveDisabled') === 'true') {
            return false;
        }
        
        return true;
    }
    
    function createSnowflakes() {
        const container = document.createElement('div');
        container.className = 'snowflakes';
        container.setAttribute('aria-hidden', 'true');
        
        const snowflakeChars = ['❄', '❅', '❆', '✻', '✼'];
        
        for (let i = 0; i < 15; i++) {
            const snowflake = document.createElement('div');
            snowflake.className = 'snowflake';
            snowflake.textContent = snowflakeChars[Math.floor(Math.random() * snowflakeChars.length)];
            container.appendChild(snowflake);
        }
        
        return container;
    }
    
    function createFestiveLights() {
        const container = document.createElement('div');
        container.className = 'festive-lights';
        container.setAttribute('aria-hidden', 'true');
        
        const colors = ['red', 'blue', 'gold', 'white'];
        const numLights = window.innerWidth < 768 ? 15 : 25;
        
        for (let i = 0; i < numLights; i++) {
            const bulb = document.createElement('div');
            bulb.className = `light-bulb ${colors[i % colors.length]}`;
            container.appendChild(bulb);
        }
        
        return container;
    }
    
    function createMenorah() {
        const menorah = document.createElement('div');
        menorah.className = 'hanukkah-menorah';
        menorah.setAttribute('aria-hidden', 'true');
        menorah.textContent = '🕎';
        return menorah;
    }
    
    function createStarSparkles() {
        const fragment = document.createDocumentFragment();
        
        for (let i = 0; i < 5; i++) {
            const star = document.createElement('div');
            star.className = 'star-sparkle';
            star.setAttribute('aria-hidden', 'true');
            star.textContent = '✡';
            fragment.appendChild(star);
        }
        
        return fragment;
    }
    
    function createCornerDecorations() {
        const fragment = document.createDocumentFragment();
        
        // Top left - Christmas tree
        const topLeft = document.createElement('div');
        topLeft.className = 'festive-corner top-left';
        topLeft.setAttribute('aria-hidden', 'true');
        topLeft.textContent = '🎄';
        fragment.appendChild(topLeft);
        
        // Top right - Dreidel
        const topRight = document.createElement('div');
        topRight.className = 'festive-corner top-right';
        topRight.setAttribute('aria-hidden', 'true');
        topRight.textContent = '🪽';
        fragment.appendChild(topRight);
        
        return fragment;
    }
    
    function createFallingGifts() {
        const container = document.createElement('div');
        container.className = 'falling-gifts';
        container.setAttribute('aria-hidden', 'true');
        
        const giftEmojis = ['🎁', '🎀', '🎄', '⭐'];
        const numGifts = window.innerWidth < 768 ? 4 : 7;
        
        for (let i = 0; i < numGifts; i++) {
            const gift = document.createElement('div');
            gift.className = 'gift';
            gift.textContent = giftEmojis[i % giftEmojis.length];
            container.appendChild(gift);
        }
        
        return container;
    }
    
    function createFallingDonuts() {
        const container = document.createElement('div');
        container.className = 'falling-donuts';
        container.setAttribute('aria-hidden', 'true');
        
        const donutEmojis = ['🍩', '🥯'];
        const numDonuts = window.innerWidth < 768 ? 3 : 6;
        
        for (let i = 0; i < numDonuts; i++) {
            const donut = document.createElement('div');
            donut.className = 'donut';
            donut.textContent = donutEmojis[i % donutEmojis.length];
            container.appendChild(donut);
        }
        
        return container;
    }
    
    function initFestive() {
        if (!shouldShowFestive()) {
            return;
        }
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', addFestiveElements);
        } else {
            addFestiveElements();
        }
    }
    
    function addFestiveElements() {
        const body = document.body;
        
        // Add all festive elements
        body.appendChild(createSnowflakes());
        body.appendChild(createFestiveLights());
        body.appendChild(createMenorah());
        body.appendChild(createStarSparkles());
        body.appendChild(createCornerDecorations());
        body.appendChild(createFallingGifts());
        body.appendChild(createFallingDonuts());
        
        // Add padding to body for lights
        const navbar = document.querySelector('.navbar.fixed-top');
        if (navbar) {
            navbar.style.top = '35px';
        }
        
        console.log('🎄🕎 Festive animations loaded! Happy Holidays!');
    }
    
    // Expose function to disable festive animations
    window.disableFestive = function() {
        localStorage.setItem('festiveDisabled', 'true');
        // Remove all festive elements
        document.querySelectorAll('.snowflakes, .festive-lights, .hanukkah-menorah, .star-sparkle, .festive-corner, .falling-gifts, .falling-donuts').forEach(el => el.remove());
        // Reset navbar position
        const navbar = document.querySelector('.navbar.fixed-top');
        if (navbar) {
            navbar.style.top = '0';
        }
    };
    
    // Expose function to re-enable festive animations
    window.enableFestive = function() {
        localStorage.removeItem('festiveDisabled');
        location.reload();
    };
    
    // Initialize
    initFestive();
})();
