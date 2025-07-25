// AttackSim JavaScript Application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Simulation interaction handlers
    initializeSimulationHandlers();
    
    // Education time tracking
    initializeTimeTracking();
});

// Simulation interaction handlers
function initializeSimulationHandlers() {
    // Handle threat reporting
    const reportButtons = document.querySelectorAll('.report-threat-btn');
    reportButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            reportThreat(this);
        });
    });

    // Handle suspicious link clicks
    const suspiciousLinks = document.querySelectorAll('.suspicious-link');
    suspiciousLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            handleSuspiciousLinkClick(this);
        });
    });

    // Handle form submissions in simulations
    const simulationForms = document.querySelectorAll('.simulation-form');
    simulationForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFormSubmission(this);
        });
    });
}

// Report threat function
function reportThreat(button) {
    const interactionId = button.dataset.interactionId;
    
    Swal.fire({
        title: 'Report Suspicious Content?',
        text: 'Are you sure this content looks suspicious?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#198754',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Yes, report it!',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (result.isConfirmed) {
            submitInteraction(interactionId, 'report_suspicious');
        }
    });
}

// Handle suspicious link clicks
function handleSuspiciousLinkClick(link) {
    const interactionId = link.dataset.interactionId;
    
    // Show immediate warning
    Swal.fire({
        title: 'Suspicious Link Detected!',
        text: 'This appears to be a malicious link. What would you like to do?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#198754',
        confirmButtonText: 'Click anyway',
        cancelButtonText: 'Don\'t click'
    }).then((result) => {
        if (result.isConfirmed) {
            submitInteraction(interactionId, 'click_link');
        } else {
            submitInteraction(interactionId, 'ignore');
        }
    });
}

// Handle form submissions
function handleFormSubmission(form) {
    const interactionId = form.dataset.interactionId;
    const formData = new FormData(form);
    
    Swal.fire({
        title: 'Submit Login Credentials?',
        text: 'Are you sure you want to submit your login information?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#0d6efd',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Submit',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (result.isConfirmed) {
            const submittedData = Object.fromEntries(formData.entries());
            submitInteraction(interactionId, 'submit_credentials', JSON.stringify(submittedData));
        }
    });
}

// Submit interaction to server
function submitInteraction(interactionId, action, submittedData = null) {
    const formData = new FormData();
    formData.append('interaction_id', interactionId);
    formData.append('action', action);
    if (submittedData) {
        formData.append('submitted_data', submittedData);
    }

    fetch('/sim/interact', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showInteractionResult(data);
        } else {
            Swal.fire('Error', data.error || 'Something went wrong', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        Swal.fire('Error', 'Failed to record interaction', 'error');
    });
}

// Show interaction result
function showInteractionResult(data) {
    const icon = data.fell_for_it ? 'warning' : 'success';
    const title = data.fell_for_it ? 'Learning Opportunity!' : 'Well Done!';
    
    Swal.fire({
        title: title,
        text: data.message,
        icon: icon,
        confirmButtonText: 'Continue',
        confirmButtonColor: '#0d6efd'
    }).then(() => {
        if (data.show_education && data.education_content) {
            showEducationalContent(data.education_content);
        }
    });
}

// Show educational content
function showEducationalContent(content) {
    Swal.fire({
        title: 'Learn More',
        html: `<div class="text-start">${content}</div>`,
        icon: 'info',
        confirmButtonText: 'Got it!',
        confirmButtonColor: '#0d6efd',
        width: '600px'
    });
}

// Time tracking for educational content
function initializeTimeTracking() {
    const educationContent = document.querySelector('.education-content');
    if (educationContent) {
        const startTime = Date.now();
        
        window.addEventListener('beforeunload', function() {
            const timeSpent = Math.floor((Date.now() - startTime) / 1000);
            const interactionId = educationContent.dataset.interactionId;
            
            if (interactionId && timeSpent > 5) { // Only track if spent more than 5 seconds
                trackEducationTime(interactionId, timeSpent);
            }
        });
    }
}

// Track education time
function trackEducationTime(interactionId, timeSpent) {
    fetch('/sim/api/track-time', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            interaction_id: interactionId,
            time_spent: timeSpent
        })
    });
}

// Get CSRF token
function getCSRFToken() {
    const token = document.querySelector('meta[name=csrf-token]');
    return token ? token.getAttribute('content') : '';
}

// Utility functions
function showNotification(message, type = 'info') {
    const toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true
    });

    toast.fire({
        icon: type,
        title: message
    });
}

// Admin-specific functions
function confirmDelete(itemName) {
    return Swal.fire({
        title: 'Are you sure?',
        text: `You won't be able to recover this ${itemName}!`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Yes, delete it!'
    });
}

// Chart initialization (for analytics)
function initializeCharts() {
    // Detection rate chart
    const detectionChart = document.getElementById('detectionChart');
    if (detectionChart) {
        const ctx = detectionChart.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Detected', 'Missed'],
                datasets: [{
                    data: [70, 30],
                    backgroundColor: ['#198754', '#dc3545'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 8;
}

// Export functions for use in other scripts
window.AttackSim = {
    reportThreat,
    submitInteraction,
    showNotification,
    confirmDelete,
    initializeCharts
}; 