// Shared JavaScript across all pages
document.addEventListener('DOMContentLoaded', () => {
    console.log('MedHub loaded');
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// API functions
async function fetchInsurancePlans() {
    try {
        const response = await fetch('/api/plans');
        return await response.json();
    } catch (error) {
        console.error('Error fetching insurance plans:', error);
        return [];
    }
}

async function fetchERWaitTimes() {
    try {
        const response = await fetch('/api/er-wait-times');
        return await response.json();
    } catch (error) {
        console.error('Error fetching ER wait times:', error);
        return [];
    }
}
