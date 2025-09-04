// Summary Page JavaScript
class SummaryManager {
    constructor() {
        this.filteredType = 'all';
        this.init();
    }
    
    init() {
        // Initialize filter buttons
        this.updateFilterButtons();
        
        // Add event listeners
        this.attachEventListeners();
        
        // Initialize tooltips if Bootstrap tooltips are available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            this.initTooltips();
        }
    }
    
    attachEventListeners() {
        // Filter button events are handled by global functions
        // Add any additional event listeners here
    }
    
    initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    updateFilterButtons() {
        const buttons = document.querySelectorAll('[id^="filter-"]');
        buttons.forEach(btn => {
            btn.classList.remove('active');
            if (btn.id === `filter-${this.filteredType}`) {
                btn.classList.add('active');
            }
        });
    }
    
    filterEventRows(type) {
        const rows = document.querySelectorAll('.event-row');
        let visibleCount = 0;
        
        rows.forEach(row => {
            const rowType = row.getAttribute('data-type');
            
            if (type === 'all' || rowType === type) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });
        
        this.updateEventCounter(visibleCount);
    }
    
    updateEventCounter(count) {
        const header = document.querySelector('.card-header h5');
        if (header) {
            const originalText = header.textContent.split('(')[0].trim();
            header.innerHTML = `
                <i class="fas fa-list me-2"></i>
                ${originalText} (${count} events)
            `;
        }
    }
    
    highlightDetectionType(type) {
        // Remove existing highlights
        document.querySelectorAll('.detection-stat').forEach(stat => {
            stat.style.border = '';
            stat.style.boxShadow = '';
        });
        
        // Highlight selected type
        if (type !== 'all') {
            const statElement = document.querySelector(`.stat-${type.replace('_', '-')}`);
            if (statElement) {
                statElement.style.border = '3px solid #007bff';
                statElement.style.boxShadow = '0 0 20px rgba(0, 123, 255, 0.3)';
            }
        }
    }
}

// Global functions
function filterEvents(type) {
    if (window.summaryManager) {
        window.summaryManager.filteredType = type;
        window.summaryManager.updateFilterButtons();
        window.summaryManager.filterEventRows(type);
        window.summaryManager.highlightDetectionType(type);
    }
}

function viewSnapshot(filename) {
    const modal = new bootstrap.Modal(document.getElementById('snapshotModal'));
    const image = document.getElementById('snapshotImage');
    const downloadLink = document.getElementById('downloadSnapshot');
    
    image.src = `/snapshot/${filename}`;
    downloadLink.href = `/snapshot/${filename}`;
    downloadLink.download = filename;
    
    modal.show();
}

function showEventDetails(eventIndex) {
    if (typeof malpracticeLog === 'undefined') {
        console.error('Malpractice log data not available');
        return;
    }
    
    const event = malpracticeLog[eventIndex];
    if (!event) {
        console.error('Event not found at index:', eventIndex);
        return;
    }
    
    const modal = new bootstrap.Modal(document.getElementById('eventDetailsModal'));
    const modalBody = document.getElementById('eventDetailsBody');
    
    const timestamp = new Date(event.timestamp);
    const detectionType = formatDetectionType(event.type);
    const confidence = Math.round(event.confidence * 100);
    
    modalBody.innerHTML = `
        <div class="event-details">
            <div class="row">
                <div class="col-sm-4"><strong>Event #:</strong></div>
                <div class="col-sm-8">${eventIndex + 1}</div>
            </div>
            <div class="row">
                <div class="col-sm-4"><strong>Type:</strong></div>
                <div class="col-sm-8">
                    <span class="badge detection-badge-${event.type}">
                        ${getDetectionIcon(event.type)} ${detectionType}
                    </span>
                </div>
            </div>
            <div class="row">
                <div class="col-sm-4"><strong>Date:</strong></div>
                <div class="col-sm-8">${timestamp.toLocaleDateString()}</div>
            </div>
            <div class="row">
                <div class="col-sm-4"><strong>Time:</strong></div>
                <div class="col-sm-8">${timestamp.toLocaleTimeString()}</div>
            </div>
            <div class="row">
                <div class="col-sm-4"><strong>Confidence:</strong></div>
                <div class="col-sm-8">
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar progress-bar-${event.type}" 
                             style="width: ${confidence}%" role="progressbar">
                            ${confidence}%
                        </div>
                    </div>
                </div>
            </div>
            ${event.snapshot ? `
                <div class="row">
                    <div class="col-sm-4"><strong>Snapshot:</strong></div>
                    <div class="col-sm-8">
                        <button type="button" class="btn btn-sm btn-outline-primary" 
                                onclick="viewSnapshot('${event.snapshot}')">
                            <i class="fas fa-image me-1"></i>View Snapshot
                        </button>
                    </div>
                </div>
            ` : ''}
            <div class="row">
                <div class="col-sm-4"><strong>Count:</strong></div>
                <div class="col-sm-8">${event.count || 'N/A'}</div>
            </div>
        </div>
    `;
    
    modal.show();
}

function printSummary() {
    // Hide non-printable elements
    const elementsToHide = document.querySelectorAll('.btn, .modal, .navbar');
    elementsToHide.forEach(el => el.style.display = 'none');
    
    // Print the page
    window.print();
    
    // Restore hidden elements
    elementsToHide.forEach(el => el.style.display = '');
}

function formatDetectionType(type) {
    const typeMap = {
        'hand_gestures': 'Suspicious Hand Gestures',
        'mobile_phone': 'Mobile Phone Usage',
        'talking': 'Talking/Mouth Movement'
    };
    return typeMap[type] || type.replace('_', ' ').toUpperCase();
}

function getDetectionIcon(type) {
    const iconMap = {
        'hand_gestures': '<i class="fas fa-hand-paper me-1"></i>',
        'mobile_phone': '<i class="fas fa-mobile-alt me-1"></i>',
        'talking': '<i class="fas fa-comments me-1"></i>'
    };
    return iconMap[type] || '<i class="fas fa-exclamation me-1"></i>';
}

// Chart functionality (if Chart.js is available)
function createSummaryChart() {
    const canvas = document.getElementById('summaryChart');
    if (!canvas || typeof Chart === 'undefined') return;
    
    const ctx = canvas.getContext('2d');
    const data = {
        labels: ['Hand Gestures', 'Mobile Phone', 'Talking'],
        datasets: [{
            data: [
                parseInt(document.getElementById('handGestureCount')?.textContent || 0),
                parseInt(document.getElementById('mobilePhoneCount')?.textContent || 0),
                parseInt(document.getElementById('talkingCount')?.textContent || 0)
            ],
            backgroundColor: ['#dc3545', '#007bff', '#ffc107'],
            borderWidth: 2,
            borderColor: '#fff'
        }]
    };
    
    new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: 'Detection Distribution'
                }
            }
        }
    });
}

// Export functionality
function exportToCSV() {
    if (typeof malpracticeLog === 'undefined') {
        console.error('Malpractice log data not available');
        return;
    }
    
    const headers = ['Event #', 'Date', 'Time', 'Detection Type', 'Confidence', 'Snapshot'];
    const csvContent = [
        headers.join(','),
        ...malpracticeLog.map((event, index) => {
            const timestamp = new Date(event.timestamp);
            return [
                index + 1,
                timestamp.toLocaleDateString(),
                timestamp.toLocaleTimeString(),
                formatDetectionType(event.type),
                Math.round(event.confidence * 100) + '%',
                event.snapshot || 'N/A'
            ].join(',');
        })
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'malpractice_report.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Search functionality
function searchEvents() {
    const searchTerm = document.getElementById('eventSearch')?.value.toLowerCase();
    if (!searchTerm) {
        filterEvents(window.summaryManager.filteredType);
        return;
    }
    
    const rows = document.querySelectorAll('.event-row');
    let visibleCount = 0;
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            row.style.display = '';
            visibleCount++;
        } else {
            row.style.display = 'none';
        }
    });
    
    if (window.summaryManager) {
        window.summaryManager.updateEventCounter(visibleCount);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.summaryManager = new SummaryManager();
    
    // Add smooth scrolling to anchors
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.animation = `fadeInUp 0.6s ease forwards ${index * 0.1}s`;
    });
    
    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeInUp {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .event-details .row {
            margin: 8px 0;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        
        .event-details .row:nth-child(even) {
            background: #e9ecef;
        }
    `;
    document.head.appendChild(style);
    
    // Initialize chart if canvas exists
    createSummaryChart();
});

// Keyboard shortcuts for summary page
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + P to print
    if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
        e.preventDefault();
        printSummary();
    }
    
    // Ctrl/Cmd + E to export PDF
    if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault();
        window.location.href = '/export_pdf';
    }
    
    // Number keys to filter (1=all, 2=gestures, 3=mobile, 4=talking)
    if (e.key >= '1' && e.key <= '4') {
        const filters = ['all', 'hand_gestures', 'mobile_phone', 'talking'];
        const filterType = filters[parseInt(e.key) - 1];
        filterEvents(filterType);
    }
});
