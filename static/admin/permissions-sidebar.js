(function() {
    'use strict';
    
    let activeCategory = null;
    let activeToggle = null;
    
    window.toggleSubmenu = function(button) {
        const group = button.closest('.nav-item-group');
        const submenu = group.querySelector('.nav-submenu');
        const category = group.dataset.category;
        const isCurrentlyExpanded = button.classList.contains('expanded');
        
        document.querySelectorAll('.nav-item-toggle.expanded').forEach(function(btn) {
            btn.classList.remove('expanded');
            btn.closest('.nav-item-group').querySelector('.nav-submenu').classList.remove('open');
        });
        
        document.querySelectorAll('.nav-item-toggle.active').forEach(function(btn) {
            btn.classList.remove('active');
        });
        
        if (!isCurrentlyExpanded) {
            button.classList.add('expanded');
            button.classList.add('active');
            submenu.classList.add('open');
            activeToggle = button;
            showCategoryPanel(category);
        } else {
            hideAllPanels();
        }
    };
    
    window.showPermission = function(permName, category) {
        showCategoryPanel(category);
        
        document.querySelectorAll('.submenu-item.active').forEach(function(item) {
            item.classList.remove('active');
        });
        
        const clickedItem = document.querySelector('a[href="#perm-' + permName + '"]');
        if (clickedItem) {
            clickedItem.classList.add('active');
        }
        
        setTimeout(function() {
            const permCard = document.getElementById('perm-' + permName);
            if (permCard) {
                permCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                
                permCard.classList.add('highlighted');
                setTimeout(function() {
                    permCard.classList.remove('highlighted');
                }, 2000);
            }
        }, 100);
    };
    
    function showCategoryPanel(category) {
        const panelId = 'panel-' + category.replace(/ /g, '-');
        
        document.querySelectorAll('.category-panel').forEach(function(panel) {
            panel.style.display = 'none';
        });
        
        const welcomeState = document.querySelector('.welcome-state');
        if (welcomeState) {
            welcomeState.style.display = 'none';
        }
        
        const panel = document.getElementById(panelId);
        if (panel) {
            panel.style.display = 'block';
            activeCategory = category;
        }
    }
    
    function hideAllPanels() {
        document.querySelectorAll('.category-panel').forEach(function(panel) {
            panel.style.display = 'none';
        });
        
        const welcomeState = document.querySelector('.welcome-state');
        if (welcomeState) {
            welcomeState.style.display = 'flex';
        }
        
        activeCategory = null;
    }
    
    document.addEventListener('DOMContentLoaded', function() {
        const firstToggle = document.querySelector('.nav-item-toggle');
        if (firstToggle) {
            toggleSubmenu(firstToggle);
        }
    });
})();
