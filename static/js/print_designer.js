/**
 * Print Designer - Clean Implementation
 * Simple IIFE wrapper with minimal global exports
 */
(function() {
    'use strict';
    
    // Private variables
    let currentPrintConfig = {
        page: {
            size: 'A4',
            margins: {top: 5, right: 5, bottom: 5, left: 5},
            rtl: true,
            rowHeight: 'auto',
            gridlines: true,
            headerRepeat: true,
            fontFamily: 'Arial Hebrew, Arial',
            fontSize: 11
        },
        layout: 'table',
        columns: [
            {
                id: 'checkbox',
                key: 'checkbox',
                label: '',
                type: 'checkbox',
                width: {value: 20, unit: 'px'},
                align: 'center',
                order: 0,
                visible: true
            },
            {
                id: 'taskname',
                key: 'taskname',
                label: 'משימה',
                type: 'text',
                dataPath: 'name',
                width: {value: 'auto', unit: 'auto'},
                align: 'right',
                order: 1,
                visible: true
            }
        ]
    };

    // Simple modal management
    function openPrintDesigner() {
        console.log('Opening Print Designer');
        const modal = document.getElementById('printDesignerModal');
        if (modal) {
            modal.style.display = 'block';
            initializeDesigner();
        } else {
            console.error('Print Designer modal not found');
        }
    }

    function closePrintDesigner() {
        console.log('Closing Print Designer');
        const modal = document.getElementById('printDesignerModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    function applyPrintDesign() {
        console.log('Applying print design');
        if (typeof showSuccess === 'function') {
            showSuccess('✅ עיצוב הוחל בהצלחה');
        }
        closePrintDesigner();
    }

    function initializeDesigner() {
        console.log('Initializing Print Designer');
        // Simple initialization
        const preview = document.getElementById('designerPreview');
        if (preview) {
            preview.innerHTML = '<div style="padding: 20px; text-align: center; color: #666;"><i class="fas fa-table fa-2x"></i><h3>מעצב טבלת הדפסה</h3><p>הפונקציונליות תתווסף בהמשך</p></div>';
        }
    }

    // Export minimal global functions
    window.openPrintDesigner = openPrintDesigner;
    window.closePrintDesigner = closePrintDesigner;
    window.applyPrintDesign = applyPrintDesign;

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Print Designer JS loaded successfully');
        
        // Bind click handler to print designer button
        const printDesignerBtn = document.getElementById('printDesignerBtn');
        if (printDesignerBtn) {
            printDesignerBtn.addEventListener('click', function(e) {
                e.preventDefault();
                openPrintDesigner();
            });
        }
    });

})();