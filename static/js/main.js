/* ============================================================================
   Inventory Management System - Main JavaScript Engine
   ============================================================================ */

document.addEventListener('DOMContentLoaded', () => {
    // Hide Loading Spinner
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        setTimeout(() => {
            spinner.style.opacity = '0';
            setTimeout(() => spinner.style.display = 'none', 300);
        }, 200);
    }

    // Dark/Light Theme Toggle
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const currentTheme = localStorage.getItem('theme') || 'dark';
    
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon(currentTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            let theme = document.documentElement.getAttribute('data-theme');
            let newTheme = theme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        if (!themeToggleBtn) return;
        const icon = themeToggleBtn.querySelector('i');
        if (icon) {
            icon.className = theme === 'dark' ? 'bi bi-sun-fill text-warning' : 'bi bi-moon-stars-fill text-primary';
        }
    }

    // Auto dismiss Toasts after 4 seconds
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.map(function (toastEl) {
        return new bootstrap.Toast(toastEl, { delay: 4000 }).show();
    });
});

// Helper Function: Global Search
function executeGlobalSearch() {
    const query = document.getElementById('global-search-input').value;
    if (query.trim().length > 0) {
        window.location.href = `/dashboard/search/?q=${encodeURIComponent(query)}`;
    }
}

// Helper Function: Print Invoice
function printInvoice() {
    window.print();
}
