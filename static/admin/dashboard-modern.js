// Modern Dashboard JavaScript

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    initDashboard();
    initAnimations();
    initCharts();
    initMap();
    initRealTimeUpdates();
    initKeyboardShortcuts();
    initTiltEffect();
});

// Dashboard Initialization
function initDashboard() {
    updateGreeting();
    animateCounters();
    startActivityFeed();
    initSearchBox();
    loadThemePreference();
}

// Update greeting based on time
function updateGreeting() {
    const hour = new Date().getHours();
    const greetingEl = document.getElementById('greeting');
    let greeting = '';
    
    if (hour < 6) greeting = '🌙 לילה טוב';
    else if (hour < 12) greeting = '☀️ בוקר טוב';
    else if (hour < 17) greeting = '🌤️ צהריים טובים';
    else if (hour < 21) greeting = '🌅 ערב טוב';
    else greeting = '🌙 לילה טוב';
    
    if (greetingEl) {
        greetingEl.textContent = greeting + ',';
    }
}

// Animate counter numbers
function animateCounters() {
    const counters = document.querySelectorAll('.counter');
    const speed = 200;
    
    counters.forEach(counter => {
        const target = +counter.getAttribute('data-target');
        const increment = target / speed;
        
        const updateCount = () => {
            const count = +counter.innerText;
            
            if (count < target) {
                counter.innerText = Math.ceil(count + increment);
                setTimeout(updateCount, 10);
            } else {
                counter.innerText = target.toLocaleString();
            }
        };
        
        updateCount();
    });
}

// Initialize animations
function initAnimations() {
    // Add stagger animation to cards
    const cards = document.querySelectorAll('.stat-card, .service-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('animate__animated', 'animate__fadeInUp');
    });
    
    // Particle animation
    createParticles();
}

// Create floating particles
function createParticles() {
    const particlesContainer = document.querySelector('.particles');
    if (!particlesContainer) return;
    
    for (let i = 0; i < 5; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.cssText = `
            position: absolute;
            width: ${Math.random() * 100 + 50}px;
            height: ${Math.random() * 100 + 50}px;
            background: radial-gradient(circle, rgba(99, 102, 241, 0.1), transparent);
            border-radius: 50%;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation: float ${20 + Math.random() * 10}s infinite ease-in-out;
            animation-delay: ${Math.random() * 5}s;
        `;
        particlesContainer.appendChild(particle);
    }
}

// Initialize Charts
function initCharts() {
    // Revenue Chart
    const revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        const revenueChart = new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
                datasets: [{
                    label: 'הכנסות',
                    data: [120, 190, 300, 850, 1200, 900, 450],
                    borderColor: 'rgb(99, 102, 241)',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₪' + value;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Revenue Sparkline
    const sparklineCtx = document.getElementById('revenueSparkline');
    if (sparklineCtx) {
        new Chart(sparklineCtx, {
            type: 'line',
            data: {
                labels: ['', '', '', '', '', '', ''],
                datasets: [{
                    data: [30, 40, 35, 50, 45, 60, 55],
                    borderColor: 'rgba(255, 255, 255, 0.8)',
                    borderWidth: 2,
                    fill: false,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                }
            }
        });
    }
}

// Initialize Map
function initMap() {
    const mapEl = document.getElementById('deliveryMap');
    if (!mapEl) return;
    
    // Initialize Leaflet map
    const map = L.map('deliveryMap').setView([32.0853, 34.7818], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // Add delivery markers
    const deliveries = [
        { lat: 32.0853, lng: 34.7818, status: 'delivered', driver: 'דוד' },
        { lat: 32.0953, lng: 34.7918, status: 'on-way', driver: 'משה' },
        { lat: 32.0753, lng: 34.7718, status: 'pending', driver: 'יוסי' }
    ];
    
    deliveries.forEach(delivery => {
        const color = delivery.status === 'delivered' ? 'green' : 
                     delivery.status === 'on-way' ? 'orange' : 'red';
        
        const marker = L.circleMarker([delivery.lat, delivery.lng], {
            color: color,
            fillColor: color,
            fillOpacity: 0.5,
            radius: 8
        }).addTo(map);
        
        marker.bindPopup(`<b>שליח: ${delivery.driver}</b><br>סטטוס: ${delivery.status}`);
    });
    
    // Animate markers
    setInterval(() => {
        deliveries.forEach(delivery => {
            if (delivery.status === 'on-way') {
                delivery.lat += (Math.random() - 0.5) * 0.001;
                delivery.lng += (Math.random() - 0.5) * 0.001;
            }
        });
    }, 3000);
}

// Real-time Updates
function initRealTimeUpdates() {
    // Simulate WebSocket connection
    setInterval(() => {
        // Update random stat
        const stats = document.querySelectorAll('.stat-number .counter');
        if (stats.length > 0) {
            const randomStat = stats[Math.floor(Math.random() * stats.length)];
            const currentValue = parseInt(randomStat.textContent);
            const change = Math.floor(Math.random() * 5) - 2;
            randomStat.textContent = Math.max(0, currentValue + change);
        }
        
        // Add new activity item
        addActivityItem();
    }, 5000);
}

// Activity Feed
let activityCounter = 1250;
function addActivityItem() {
    const timeline = document.getElementById('activityTimeline');
    if (!timeline) return;
    
    const activities = [
        { icon: 'fa-cart-plus', type: 'new-order', text: `הזמנה חדשה #${activityCounter++}`, meta: `₪${Math.floor(Math.random() * 200 + 50)}` },
        { icon: 'fa-credit-card', type: 'payment', text: 'תשלום התקבל', meta: 'Apple Pay' },
        { icon: 'fa-truck', type: 'delivery', text: 'משלוח יצא', meta: 'דוד השליח' },
        { icon: 'fa-check-circle', type: 'completed', text: 'הזמנה הושלמה', meta: 'זמן: 22 דקות' }
    ];
    
    const activity = activities[Math.floor(Math.random() * activities.length)];
    
    const item = document.createElement('div');
    item.className = `timeline-item ${activity.type} animate__animated animate__slideInRight`;
    item.innerHTML = `
        <span class="timeline-icon"><i class="fas ${activity.icon}"></i></span>
        <div class="timeline-content">
            <strong>${activity.text}</strong>
            <span class="timeline-meta">עכשיו • ${activity.meta}</span>
        </div>
        ${activity.type === 'new-order' ? '<span class="timeline-badge">חדש</span>' : ''}
    `;
    
    timeline.insertBefore(item, timeline.firstChild);
    
    // Remove old items
    if (timeline.children.length > 10) {
        timeline.removeChild(timeline.lastChild);
    }
}

function startActivityFeed() {
    // Initial items
    for (let i = 0; i < 3; i++) {
        setTimeout(() => addActivityItem(), i * 500);
    }
}

// Theme Toggle
function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    const icon = document.getElementById('themeIcon');
    if (icon) {
        icon.className = document.body.classList.contains('dark-mode') ? 'fas fa-sun' : 'fas fa-moon';
    }
    localStorage.setItem('theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
}

function loadThemePreference() {
    const theme = localStorage.getItem('theme');
    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
        const icon = document.getElementById('themeIcon');
        if (icon) icon.className = 'fas fa-sun';
    }
}

// Search Box
function initSearchBox() {
    const searchInput = document.getElementById('globalSearch');
    const searchResults = document.getElementById('searchResults');
    
    if (!searchInput) return;
    
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        if (query.length > 2) {
            // Simulate search results
            searchResults.innerHTML = `
                <div class="search-result">
                    <i class="fas fa-receipt"></i>
                    <span>הזמנה #1247</span>
                </div>
                <div class="search-result">
                    <i class="fas fa-user"></i>
                    <span>לקוח: משה כהן</span>
                </div>
                <div class="search-result">
                    <i class="fas fa-utensils"></i>
                    <span>פיצה מרגריטה</span>
                </div>
            `;
            searchResults.style.display = 'block';
        } else {
            searchResults.style.display = 'none';
        }
    });
    
    // Close search results when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-box')) {
            searchResults.style.display = 'none';
        }
    });
}

// Keyboard Shortcuts
function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl+K for search
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            document.getElementById('globalSearch')?.focus();
        }
        
        // Ctrl+N for new order
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            quickNewOrder();
        }
        
        // Ctrl+D for dark mode
        if (e.ctrlKey && e.key === 'd') {
            e.preventDefault();
            toggleTheme();
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            closeAllModals();
        }
        
        // ? for shortcuts help
        if (e.key === '?' && !e.target.matches('input, textarea')) {
            showShortcuts();
        }
    });
}

// Tilt Effect
function initTiltEffect() {
    VanillaTilt.init(document.querySelectorAll("[data-tilt]"), {
        max: 10,
        speed: 400,
        glare: true,
        "max-glare": 0.2
    });
}

// Toggle Functions
function toggleSidebar() {
    document.querySelector('.sidebar-modern')?.classList.toggle('collapsed');
}

function toggleNotifications() {
    const panel = document.getElementById('notificationPanel');
    if (panel) {
        panel.classList.toggle('active');
    }
}

function toggleFAB() {
    document.querySelector('.fab-container')?.classList.toggle('active');
}

function toggleAI() {
    const assistant = document.getElementById('aiAssistant');
    if (assistant) {
        assistant.classList.toggle('active');
    }
}

function toggleAutoScroll() {
    // Implementation for auto-scroll toggle
    const btn = event.target.closest('button');
    const icon = btn.querySelector('i');
    if (icon.classList.contains('fa-pause')) {
        icon.className = 'fas fa-play';
        btn.innerHTML = '<i class="fas fa-play"></i> המשך גלילה';
    } else {
        icon.className = 'fas fa-pause';
        btn.innerHTML = '<i class="fas fa-pause"></i> עצור גלילה';
    }
}

// Navigation
function navigateTo(section) {
    const routes = {
        'orders': '/admin/orders-management',
        'payments': '/admin/payment-config',
        'kitchen': '/admin/kitchen-config',
        'delivery': '/admin/drivers-management',
        'customers': '/admin/customers-management',
        'settings': '/admin/system-config'
    };
    
    if (routes[section]) {
        window.location.href = routes[section];
    }
}

// Quick Actions
function quickNewOrder() {
    alert('פתיחת טופס הזמנה חדשה...');
    // Implementation for new order form
}

function viewAllOrders() {
    window.location.href = '/admin/orders-management';
}

function clearNotifications() {
    const list = document.querySelector('.notification-list');
    if (list) {
        list.innerHTML = '<p style="text-align: center; padding: 2rem; color: #94a3b8;">אין התראות חדשות</p>';
    }
}

function showShortcuts() {
    const modal = document.getElementById('shortcutsModal');
    if (modal) {
        modal.classList.add('active');
    }
}

function closeAllModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.remove('active');
    });
    document.getElementById('notificationPanel')?.classList.remove('active');
    document.getElementById('aiAssistant')?.classList.remove('active');
}

// AI Assistant
function sendToAI() {
    const input = document.getElementById('aiInput');
    const messages = document.querySelector('.ai-messages');
    
    if (!input || !messages) return;
    
    const userMessage = input.value.trim();
    if (!userMessage) return;
    
    // Add user message
    const userDiv = document.createElement('div');
    userDiv.className = 'ai-message user';
    
    const iconSpan = document.createElement('span');
    iconSpan.className = 'ai-icon';
    iconSpan.textContent = '👤';
    
    const messagePara = document.createElement('p');
    messagePara.textContent = userMessage;
    
    userDiv.appendChild(iconSpan);
    userDiv.appendChild(messagePara);
    messages.appendChild(userDiv);
    
    // Clear input
    input.value = '';
    
    // Simulate AI response
    setTimeout(() => {
        const aiDiv = document.createElement('div');
        aiDiv.className = 'ai-message';
        aiDiv.innerHTML = `
            <span class="ai-icon">🤖</span>
            <p>אני מעבד את הבקשה שלך...</p>
        `;
        messages.appendChild(aiDiv);
        messages.scrollTop = messages.scrollHeight;
    }, 500);
}

// Map Functions
function centerMap() {
    // Center map on restaurant location
    if (window.deliveryMap) {
        window.deliveryMap.setView([32.0853, 34.7818], 13);
    }
}

function toggleHeatmap() {
    // Toggle heatmap overlay
    alert('מצב מפת חום');
}

// Chart Tab Switching
document.addEventListener('click', (e) => {
    if (e.target.matches('.tab-btn')) {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        e.target.classList.add('active');
        
        // Update chart data based on period
        const period = e.target.dataset.period;
        updateChartData(period);
    }
});

function updateChartData(period) {
    // Implementation for updating chart based on period
    console.log('Updating chart for period:', period);
}

// Auto-refresh data every 30 seconds
setInterval(() => {
    // Refresh dashboard data
    console.log('Refreshing dashboard data...');
    // Implementation for data refresh
}, 30000);

// WebSocket for real-time updates (mock)
function initWebSocket() {
    // In production, connect to real WebSocket server
    console.log('WebSocket initialized for real-time updates');
}

// Initialize WebSocket
initWebSocket();

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', () => {
        const perfData = window.performance.timing;
        const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
        console.log(`Page load time: ${pageLoadTime}ms`);
    });
}