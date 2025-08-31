// Sidebar Menu Functions

// Toggle Sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('sidebarMenu');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (!sidebar) return;
    
    sidebar.classList.toggle('active');
    
    // Create overlay if it doesn't exist
    if (!overlay) {
        const newOverlay = document.createElement('div');
        newOverlay.id = 'sidebarOverlay';
        newOverlay.className = 'sidebar-overlay';
        newOverlay.onclick = toggleSidebar;
        document.body.appendChild(newOverlay);
    }
    
    document.getElementById('sidebarOverlay').classList.toggle('active');
}

// Toggle section in sidebar
function toggleSection(element) {
    const section = element.parentElement;
    section.classList.toggle('expanded');
    
    // Close other sections
    const allSections = document.querySelectorAll('.nav-section');
    allSections.forEach(sec => {
        if (sec !== section) {
            sec.classList.remove('expanded');
        }
    });
}

// Initialize sidebar on page load
document.addEventListener('DOMContentLoaded', function() {
    // Auto-expand first section
    const firstSection = document.querySelector('.nav-section');
    if (firstSection) {
        firstSection.classList.add('expanded');
    }
    
    // Mark current page as active
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        if (item.getAttribute('href') === currentPath) {
            item.classList.add('active');
            // Expand parent section if exists
            const parentSection = item.closest('.nav-section');
            if (parentSection) {
                parentSection.classList.add('expanded');
            }
        }
    });
});