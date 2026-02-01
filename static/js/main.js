/**
 * Main JavaScript file for the Raw Material Procurement Mediator
 * Handles interactive features and UI enhancements
 */

// Global application object
const ProcurementApp = {
    // Initialize the application
    init: function() {
        this.setupEventListeners();
        this.initializeTooltips();
        this.setupFormValidation();
    },

    // Setup global event listeners
    setupEventListeners: function() {
        // Handle form submissions with loading states
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', this.handleFormSubmit);
        });

        // Handle table sorting if tables exist
        document.querySelectorAll('table.sortable th').forEach(header => {
            header.addEventListener('click', this.handleTableSort);
        });

        // Auto-hide alerts after 5 seconds
        setTimeout(() => {
            document.querySelectorAll('.alert').forEach(alert => {
                if (alert.classList.contains('alert-success')) {
                    this.fadeOut(alert);
                }
            });
        }, 5000);
    },

    // Initialize Bootstrap tooltips
    initializeTooltips: function() {
        if (typeof bootstrap !== 'undefined') {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    },

    // Setup form validation
    setupFormValidation: function() {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    },

    // Handle form submission with loading states
    handleFormSubmit: function(event) {
        const form = event.target;
        const submitButton = form.querySelector('button[type="submit"]');

        if (submitButton) {
            // Store original button content
            const originalContent = submitButton.innerHTML;

            // Show loading state
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...';
            submitButton.disabled = true;

            // Reset button after 30 seconds (fallback)
            setTimeout(() => {
                submitButton.innerHTML = originalContent;
                submitButton.disabled = false;
            }, 30000);
        }
    },

    // Handle table sorting
    handleTableSort: function(event) {
        const header = event.target;
        const table = header.closest('table');
        const column = Array.from(header.parentNode.children).indexOf(header);
        const rows = Array.from(table.querySelectorAll('tbody tr'));

        // Determine sort direction
        const isAscending = !header.classList.contains('sort-asc');

        // Remove existing sort classes
        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });

        // Add new sort class
        header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');

        // Sort rows
        rows.sort((a, b) => {
            const aValue = a.children[column].textContent.trim();
            const bValue = b.children[column].textContent.trim();

            // Try to parse as numbers
            const aNum = parseFloat(aValue.replace(/[^0-9.-]/g, ''));
            const bNum = parseFloat(bValue.replace(/[^0-9.-]/g, ''));

            if (!isNaN(aNum) && !isNaN(bNum)) {
                return isAscending ? aNum - bNum : bNum - aNum;
            } else {
                return isAscending ? 
                    aValue.localeCompare(bValue) : 
                    bValue.localeCompare(aValue);
            }
        });

        // Reorder DOM elements
        const tbody = table.querySelector('tbody');
        rows.forEach(row => tbody.appendChild(row));
    },

    // Utility function to fade out element
    fadeOut: function(element) {
        element.style.transition = 'opacity 0.5s';
        element.style.opacity = '0';
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }, 500);
    },

    // Format currency values
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },

    // Format large numbers
    formatNumber: function(number) {
        return new Intl.NumberFormat('en-US').format(number);
    },

    // Show loading overlay
    showLoading: function() {
        const overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
        overlay.style.backgroundColor = 'rgba(0,0,0,0.5)';
        overlay.style.zIndex = '9999';
        overlay.innerHTML = `
            <div class="text-center text-white">
                <i class="fas fa-spinner fa-spin fa-3x mb-3"></i>
                <h4>Processing Request...</h4>
                <p>Please wait while we analyze vendors</p>
            </div>
        `;
        document.body.appendChild(overlay);
    },

    // Hide loading overlay
    hideLoading: function() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
};

// Vendor-specific functions
const VendorAnalysis = {
    // Compare two vendors
    compareVendors: function(vendor1Id, vendor2Id) {
        // This would make an API call to compare vendors
        console.log(`Comparing vendors: ${vendor1Id} vs ${vendor2Id}`);
        // Implementation would go here
    },

    // Get vendor details
    getVendorDetails: function(vendorId) {
        return fetch(`/api/vendor/${vendorId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    return data.vendor;
                } else {
                    throw new Error(data.error);
                }
            })
            .catch(error => {
                console.error('Error fetching vendor details:', error);
                this.showError('Failed to load vendor details');
            });
    },

    // Show error message
    showError: function(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(alert, container.firstChild);
        }
    },

    // Show success message
    showSuccess: function(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(alert, container.firstChild);
        }
    }
};

// Chart utilities
const ChartUtils = {
    // Default chart colors
    colors: {
        primary: 'rgba(13, 110, 253, 0.8)',
        success: 'rgba(25, 135, 84, 0.8)',
        warning: 'rgba(255, 193, 7, 0.8)',
        danger: 'rgba(220, 53, 69, 0.8)',
        info: 'rgba(13, 202, 240, 0.8)'
    },

    // Create a score comparison chart
    createScoreChart: function(canvasId, vendors) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: vendors.map(v => v.name.length > 15 ? v.name.substr(0, 15) + '...' : v.name),
                datasets: [{
                    label: 'Overall Score',
                    data: vendors.map(v => v.total_score),
                    backgroundColor: vendors.map((v, i) => i === 0 ? this.colors.success : this.colors.primary),
                    borderColor: vendors.map((v, i) => i === 0 ? 'rgba(25, 135, 84, 1)' : 'rgba(13, 110, 253, 1)'),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
};

function generateReport() {
    // Placeholder for analytics report
    alert('Analytics report generation will be implemented in a future update.');
}

// Functions for navbar links
function showVendorComparison() {
    // Show vendor comparison modal or redirect
    alert('Vendor comparison feature will be implemented in a future update. For now, you can compare vendors in the analysis results page.');
}

function showReports() {
    // Show reports page or modal
    alert('Reports feature will be implemented in a future update.');
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    ProcurementApp.init();
});

// Export for global access
window.ProcurementApp = ProcurementApp;
window.VendorAnalysis = VendorAnalysis;
window.ChartUtils = ChartUtils;