// Monitoring Page JavaScript
class MonitoringSystem {
    constructor() {
        this.sessionStartTime = new Date();
        this.alertsContainer = document.getElementById('alertsContainer');
        this.updateInterval = null;
        this.maxAlerts = 50; // Maximum number of alerts to show
        
        this.init();
    }
    
    init() {
        // Update current time display
        this.updateCurrentTime();
        setInterval(() => this.updateCurrentTime(), 1000);
        
        // Update session duration
        this.updateSessionDuration();
        setInterval(() => this.updateSessionDuration(), 1000);
        
        // Start polling for alerts
        this.startAlertsPolling();
        
        // Set session start time
        document.getElementById('sessionStart').textContent = 
            this.sessionStartTime.toLocaleTimeString();
    }
    
    updateCurrentTime() {
        const now = new Date();
        document.getElementById('currentTime').textContent = 
            now.toLocaleTimeString();
    }
    
    updateSessionDuration() {
        const now = new Date();
        const duration = now - this.sessionStartTime;
        const hours = Math.floor(duration / (1000 * 60 * 60));
        const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((duration % (1000 * 60)) / 1000);
        
        const durationStr = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        document.getElementById('sessionDuration').textContent = durationStr;
    }
    
    startAlertsPolling() {
        // Initial load
        this.fetchAlerts();
        
        // Poll every 2 seconds
        this.updateInterval = setInterval(() => {
            this.fetchAlerts();
        }, 2000);
    }
    
    async fetchAlerts() {
        try {
            const response = await fetch('/get_alerts');
            if (response.ok) {
                const data = await response.json();
                this.updateStatistics(data.counts, data.total_events);
                this.updateAlerts(data.alerts);
                this.updateDetectionRate(data.total_events);
            }
        } catch (error) {
            console.error('Error fetching alerts:', error);
        }
    }
    
    updateStatistics(counts, totalEvents) {
        document.getElementById('handGestureCount').textContent = counts.hand_gestures || 0;
        document.getElementById('mobilePhoneCount').textContent = counts.mobile_phone || 0;
        document.getElementById('talkingCount').textContent = counts.talking || 0;
        document.getElementById('totalEvents').textContent = totalEvents || 0;
    }
    
    updateAlerts(alerts) {
        // Keep only recent alerts (last 10)
        const recentAlerts = alerts.slice(-10);
        
        // Clear existing alerts except the initial message if no alerts exist
        if (recentAlerts.length > 0) {
            this.alertsContainer.innerHTML = '';
        }
        
        // Add new alerts
        recentAlerts.forEach(alert => {
            this.addAlertToContainer(alert);
        });
        
        // Scroll to bottom to show latest alerts
        this.alertsContainer.scrollTop = this.alertsContainer.scrollHeight;
    }
    
    addAlertToContainer(alert) {
        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-detection ${alert.type}`;
        
        const timestamp = new Date(alert.timestamp).toLocaleTimeString();
        const detectionType = this.formatDetectionType(alert.type);
        const confidence = Math.round(alert.confidence * 100);
        
        alertElement.innerHTML = `
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <strong>${detectionType}</strong>
                    <br>
                    <small class="text-muted">${timestamp}</small>
                </div>
                <div class="text-end">
                    <span class="badge bg-secondary">${confidence}%</span>
                    ${alert.snapshot ? '<i class="fas fa-camera text-success ms-1"></i>' : ''}
                </div>
            </div>
        `;
        
        // Add animation class
        alertElement.style.animation = 'slideIn 0.5s ease-in-out';
        
        this.alertsContainer.appendChild(alertElement);
        
        // Remove old alerts if too many
        while (this.alertsContainer.children.length > this.maxAlerts) {
            this.alertsContainer.removeChild(this.alertsContainer.firstChild);
        }
    }
    
    updateDetectionRate(totalEvents) {
        const now = new Date();
        const durationMinutes = (now - this.sessionStartTime) / (1000 * 60);
        const rate = durationMinutes > 0 ? (totalEvents / durationMinutes).toFixed(1) : '0.0';
        document.getElementById('detectionRate').textContent = `${rate}/min`;
    }
    
    formatDetectionType(type) {
        const typeMap = {
            'hand_gestures': 'Suspicious Hand Gesture',
            'mobile_phone': 'Mobile Phone Detected',
            'talking': 'Talking Detected'
        };
        return typeMap[type] || type.replace('_', ' ').toUpperCase();
    }
    
    stopPolling() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
}

// Global functions
function stopMonitoring() {
    // Show confirmation modal
    const modal = new bootstrap.Modal(document.getElementById('stopModal'));
    modal.show();
}

function refreshAlerts() {
    if (window.monitoringSystem) {
        window.monitoringSystem.fetchAlerts();
        
        // Show refresh feedback
        const refreshBtn = event.target;
        const originalHTML = refreshBtn.innerHTML;
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Refreshing...';
        refreshBtn.disabled = true;
        
        setTimeout(() => {
            refreshBtn.innerHTML = originalHTML;
            refreshBtn.disabled = false;
        }, 1000);
    }
}

function exportCurrentSession() {
    // This would trigger a download of current session data
    window.open('/export_pdf', '_blank');
}

// Add some visual feedback for user interactions
document.addEventListener('DOMContentLoaded', function() {
    // Initialize monitoring system
    window.monitoringSystem = new MonitoringSystem();
    
    // Add click effects to buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.5);
                transform: scale(0);
                animation: ripple 0.6s linear;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
    
    // Add CSS for ripple animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
});

// Handle page unload
window.addEventListener('beforeunload', function() {
    if (window.monitoringSystem) {
        window.monitoringSystem.stopPolling();
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Q to stop monitoring
    if ((e.ctrlKey || e.metaKey) && e.key === 'q') {
        e.preventDefault();
        stopMonitoring();
    }
    
    // F5 to refresh alerts
    if (e.key === 'F5') {
        e.preventDefault();
        refreshAlerts();
    }
    
    // Ctrl/Cmd + E to export
    if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault();
        exportCurrentSession();
    }
});

// Add connection status monitoring
function checkConnection() {
    fetch('/get_alerts')
        .then(() => {
            // Connection is good
            document.querySelector('.status-indicator').innerHTML = 
                '<i class="fas fa-eye text-success"></i> AI MONITORING ACTIVE';
        })
        .catch(() => {
            // Connection lost
            document.querySelector('.status-indicator').innerHTML = 
                '<i class="fas fa-exclamation-triangle text-warning"></i> CONNECTION LOST';
        });
}

// Check connection every 10 seconds
setInterval(checkConnection, 10000);
