/**
 * Camera controls functionality
 */
const CameraControls = {
    /**
     * Update shutter speed display based on slider value
     * @param {number} sliderValue - Value from the exposure slider (0-1000)
     */
    updateShutter: function(sliderValue) {
        const minUs = 100;
        const maxUs = 200000000;
        const us = minUs * Math.pow(maxUs / minUs, sliderValue / 1000);
        const seconds = us / 1000000;
        const display = seconds < 1 ? 
            '1/' + Math.round(1/seconds) + 's' : 
            Math.round(seconds) + 's';
        
        document.getElementById('shutter_display').value = display;
    },
    
    /**
     * Monitor capture progress without starting a separate countdown
     * @param {number} expectedSeconds - Expected exposure time in seconds
     */
    monitorCapture: function(expectedSeconds) {
        // Start polling for status immediately
        this.pollCaptureStatus();
    },
    
    /**
     * Poll for capture status until completion
     */
    pollCaptureStatus: function() {
        const countdownElement = document.getElementById('countdown');
        const statusElement = document.getElementById('status_display');
        let lastStatus = '';
        let hasStartedCapture = false;
        
        // Poll every 500ms to check capture status
        let statusCheck = setInterval(function() {
            fetch('/capture_status', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                // Only update if status has changed
                if (lastStatus !== data.capture_status) {
                    lastStatus = data.capture_status;
                    
                    // Update status display
                    if (statusElement) {
                        statusElement.textContent = data.capture_status;
                    }
                    
                    // Handle countdown display based on status
                    if (countdownElement) {
                        if (data.capture_status.includes("Capturing")) {
                            // Just started capturing
                            hasStartedCapture = true;
                        } 
                        else if (data.capture_status.includes("saved as")) {
                            // Capture complete
                            countdownElement.textContent = '';
                            clearInterval(statusCheck);
                        } 
                        else if (hasStartedCapture) {
                            // In progress, show appropriate message
                            countdownElement.textContent = 'Processing...';
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error checking capture status:', error);
            });
        }, 300);
    },
    
    /**
     * Toggle digital gain controls
     * @param {HTMLElement} checkbox - The digital gain checkbox
     */
    toggleDigitalGain: function(checkbox) {
        const slider = document.querySelector('input[name="digital_gain"]');
        const container = document.getElementById('digital-gain-container');
        
        slider.disabled = !checkbox.checked;
        container.style.opacity = checkbox.checked ? '1.0' : '0.5';
    }
};

// Initialize controls when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Set up event handler for digital gain checkbox
    const checkbox = document.querySelector('input[name="use_digital_gain"]');
    if (checkbox) {
        checkbox.addEventListener('change', function() {
            CameraControls.toggleDigitalGain(this);
        });
    }
    
    // Set up capture form with status monitoring
    const captureForm = document.getElementById('capture-form');
    if (captureForm) {
        captureForm.addEventListener('submit', function(event) {
            // Get exposure seconds from data attribute
            const seconds = parseInt(this.getAttribute('data-exposure-seconds'), 10);
            if (!isNaN(seconds)) {
                CameraControls.monitorCapture(seconds);
            }
            // Allow form submission to continue
            return true;
        });
    }
});