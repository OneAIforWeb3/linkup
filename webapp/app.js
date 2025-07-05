// Telegram Mini App Configuration
const tg = window.Telegram.WebApp;
const API_BASE_URL = window.location.origin.includes('localhost') 
    ? 'http://localhost:8000' 
    : 'https://your-api-domain.com';

// Global State
let currentUser = null;
let currentUserProfile = null;
let connections = [];
let qrCodeData = null;

// Initialize the app
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Initialize Telegram WebApp
        tg.ready();
        tg.expand();
        
        // Set up the app theme
        setAppTheme();
        
        // Get user data from Telegram
        await initializeUser();
        
        // Set up event listeners
        setupEventListeners();
        
        // Load initial data
        await loadUserProfile();
        await loadConnections();
        await generateQRCode();
        
        // Hide loading overlay
        hideLoading();
        
    } catch (error) {
        console.error('Error initializing app:', error);
        showToast('Error initializing app. Please try again.', 'error');
        hideLoading();
    }
});

// Set app theme based on Telegram theme
function setAppTheme() {
    const root = document.documentElement;
    
    // Set Telegram theme variables
    if (tg.themeParams) {
        root.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color || '#ffffff');
        root.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color || '#000000');
        root.style.setProperty('--tg-theme-hint-color', tg.themeParams.hint_color || '#999999');
        root.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color || '#007bff');
        root.style.setProperty('--tg-theme-button-text-color', tg.themeParams.button_text_color || '#ffffff');
        root.style.setProperty('--tg-theme-secondary-bg-color', tg.themeParams.secondary_bg_color || '#f8f9fa');
    }
}

// Initialize user from Telegram data
async function initializeUser() {
    if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
        currentUser = tg.initDataUnsafe.user;
        
        // Update UI with user info
        updateUserHeader();
        
        // Create or update user in database
        await createOrUpdateUser();
    } else {
        // For testing purposes, create a mock user
        currentUser = {
            id: 12345,
            first_name: 'Test',
            last_name: 'User',
            username: 'testuser',
            photo_url: 'https://via.placeholder.com/150'
        };
        updateUserHeader();
    }
}

// Update user header with Telegram info
function updateUserHeader() {
    const userName = document.getElementById('userName');
    const userAvatar = document.getElementById('userAvatar');
    
    if (currentUser) {
        const fullName = `${currentUser.first_name} ${currentUser.last_name || ''}`.trim();
        userName.textContent = fullName;
        
        if (currentUser.photo_url) {
            userAvatar.src = currentUser.photo_url;
        } else {
            userAvatar.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(fullName)}&background=667eea&color=fff`;
        }
    }
}

// Create or update user in database
async function createOrUpdateUser() {
    try {
        const userData = {
            tg_id: currentUser.id,
            username: currentUser.username || '',
            display_name: `${currentUser.first_name} ${currentUser.last_name || ''}`.trim(),
            profile_image_url: currentUser.photo_url || ''
        };
        
        const response = await fetch(`${API_BASE_URL}/create-user`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('User created/updated:', result);
        }
    } catch (error) {
        console.error('Error creating/updating user:', error);
    }
}

// Load user profile from database
async function loadUserProfile() {
    try {
        const response = await fetch(`${API_BASE_URL}/get-user-by-tg-id?tg_id=${currentUser.id}`);
        
        if (response.ok) {
            const profile = await response.json();
            currentUserProfile = profile;
            populateProfileForm(profile);
            updateUserRole(profile.role);
        }
    } catch (error) {
        console.error('Error loading user profile:', error);
    }
}

// Populate profile form with user data
function populateProfileForm(profile) {
    if (profile) {
        document.getElementById('displayName').value = profile.display_name || '';
        document.getElementById('role').value = profile.role || '';
        document.getElementById('projectName').value = profile.project_name || '';
        document.getElementById('description').value = profile.description || '';
    }
}

// Update user role in header
function updateUserRole(role) {
    const userRole = document.getElementById('userRole');
    userRole.textContent = role || 'Set your role';
}

// Load user connections
async function loadConnections() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/user-connections?tg_id=${currentUser.id}`);
        
        if (response.ok) {
            connections = await response.json();
            updateConnectionsCount();
            displayConnections();
        }
    } catch (error) {
        console.error('Error loading connections:', error);
        connections = [];
    }
}

// Update connections count in UI
function updateConnectionsCount() {
    const connectionCount = document.getElementById('connectionCount');
    const groupCount = document.getElementById('groupCount');
    
    connectionCount.textContent = connections.length;
    groupCount.textContent = Math.floor(connections.length / 2); // Rough estimate
}

// Display connections in the UI
function displayConnections() {
    const connectionsList = document.getElementById('connectionsList');
    
    if (connections.length === 0) {
        connectionsList.innerHTML = '<p class="no-connections">No connections yet. Start networking!</p>';
        return;
    }
    
    connectionsList.innerHTML = connections.map(connection => `
        <div class="connection-card">
            <div class="connection-header">
                <img src="${connection.profile_image_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(connection.display_name)}&background=667eea&color=fff`}" 
                     alt="${connection.display_name}" class="connection-avatar">
                <div>
                    <div class="connection-name">${connection.display_name}</div>
                    <div class="connection-role">${connection.role || 'No role specified'}</div>
                </div>
            </div>
            <p class="connection-project">${connection.project_name || 'No project specified'}</p>
            <p class="connection-description">${connection.description || 'No description'}</p>
        </div>
    `).join('');
}

// Generate QR code
async function generateQRCode() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/generate-qr?tg_id=${currentUser.id}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const qrImageUrl = URL.createObjectURL(blob);
            
            const qrImage = document.getElementById('qrImage');
            qrImage.src = qrImageUrl;
            qrImage.style.display = 'block';
            
            // Store QR data for sharing
            qrCodeData = qrImageUrl;
        }
    } catch (error) {
        console.error('Error generating QR code:', error);
        showToast('Error generating QR code', 'error');
    }
}

// Set up event listeners
function setupEventListeners() {
    // Tab switching
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab;
            switchTab(tabId);
        });
    });
    
    // Profile form submission
    const profileForm = document.getElementById('profileForm');
    profileForm.addEventListener('submit', handleProfileSubmit);
    
    // QR code actions
    document.getElementById('shareQR').addEventListener('click', shareQRCode);
    document.getElementById('downloadQR').addEventListener('click', downloadQRCode);
    document.getElementById('regenerateQR').addEventListener('click', regenerateQRCode);
    
    // Connection actions
    document.getElementById('scanQR').addEventListener('click', scanQRCode);
    document.getElementById('createGroup').addEventListener('click', createGroup);
    
    // Header share button
    document.getElementById('shareBtn').addEventListener('click', shareProfile);
}

// Switch between tabs
function switchTab(tabId) {
    // Update tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    
    // Update tab content
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => content.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    
    // Haptic feedback
    if (tg.HapticFeedback) {
        tg.HapticFeedback.impactOccurred('light');
    }
}

// Handle profile form submission
async function handleProfileSubmit(e) {
    e.preventDefault();
    
    showLoading();
    
    try {
        const formData = {
            tg_id: currentUser.id,
            display_name: document.getElementById('displayName').value,
            role: document.getElementById('role').value,
            project_name: document.getElementById('projectName').value,
            description: document.getElementById('description').value
        };
        
        const response = await fetch(`${API_BASE_URL}/api/update-profile`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            currentUserProfile = { ...currentUserProfile, ...formData };
            updateUserRole(formData.role);
            showToast('Profile updated successfully!', 'success');
            
            // Regenerate QR code with updated profile
            await generateQRCode();
        } else {
            throw new Error('Failed to update profile');
        }
    } catch (error) {
        console.error('Error updating profile:', error);
        showToast('Error updating profile. Please try again.', 'error');
    }
    
    hideLoading();
}

// Share QR code
async function shareQRCode() {
    if (qrCodeData) {
        try {
            // Convert blob URL to actual blob for sharing
            const response = await fetch(qrCodeData);
            const blob = await response.blob();
            
            if (navigator.share) {
                await navigator.share({
                    title: 'My LinkUp QR Code',
                    text: 'Scan this QR code to connect with me on LinkUp!',
                    files: [new File([blob], 'linkup-qr.png', { type: 'image/png' })]
                });
            } else if (tg.shareMessage) {
                tg.shareMessage('Check out my LinkUp QR code!');
            } else {
                // Fallback: copy to clipboard
                navigator.clipboard.writeText('Check out my LinkUp QR code!');
                showToast('QR code info copied to clipboard!', 'success');
            }
        } catch (error) {
            console.error('Error sharing QR code:', error);
            showToast('Error sharing QR code', 'error');
        }
    }
}

// Download QR code
async function downloadQRCode() {
    if (qrCodeData) {
        const link = document.createElement('a');
        link.download = 'linkup-qr-code.png';
        link.href = qrCodeData;
        link.click();
        showToast('QR code downloaded!', 'success');
    }
}

// Regenerate QR code with customization
async function regenerateQRCode() {
    const theme = document.getElementById('qrTheme').value;
    const color = document.getElementById('qrColor').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/generate-qr?tg_id=${currentUser.id}&theme=${theme}&color=${encodeURIComponent(color)}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const qrImageUrl = URL.createObjectURL(blob);
            
            const qrImage = document.getElementById('qrImage');
            qrImage.src = qrImageUrl;
            qrCodeData = qrImageUrl;
            
            showToast('QR code regenerated!', 'success');
        }
    } catch (error) {
        console.error('Error regenerating QR code:', error);
        showToast('Error regenerating QR code', 'error');
    }
}

// Scan QR code
function scanQRCode() {
    if (tg.showScanQrPopup) {
        tg.showScanQrPopup({
            text: 'Scan a LinkUp QR code to connect'
        }, (qrText) => {
            if (qrText) {
                handleScannedQR(qrText);
            }
        });
    } else {
        // Fallback: show input dialog
        const qrText = prompt('Enter QR code data:');
        if (qrText) {
            handleScannedQR(qrText);
        }
    }
}

// Handle scanned QR code
async function handleScannedQR(qrText) {
    try {
        const response = await fetch(`${API_BASE_URL}/scan-qr`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                scanner_tg_id: currentUser.id,
                qr_data: qrText
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            showToast(`Connected with ${result.connected_user}!`, 'success');
            
            // Reload connections
            await loadConnections();
            
            // Switch to connections tab
            switchTab('connections');
        } else {
            throw new Error('Failed to process QR code');
        }
    } catch (error) {
        console.error('Error processing scanned QR:', error);
        showToast('Error processing QR code', 'error');
    }
}

// Create group with connections
async function createGroup() {
    if (connections.length === 0) {
        showToast('No connections to create a group with', 'info');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/create-group`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                creator_tg_id: currentUser.id,
                participant_tg_ids: connections.map(c => c.tg_id)
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            showToast('Group created successfully!', 'success');
            
            // Update group count
            updateConnectionsCount();
        } else {
            throw new Error('Failed to create group');
        }
    } catch (error) {
        console.error('Error creating group:', error);
        showToast('Error creating group', 'error');
    }
}

// Share profile
function shareProfile() {
    const profileText = `Check out my LinkUp profile!\n\n${currentUserProfile?.display_name || 'LinkUp User'}\n${currentUserProfile?.role || ''}\n${currentUserProfile?.project_name || ''}\n\nConnect with me on LinkUp!`;
    
    if (tg.shareMessage) {
        tg.shareMessage(profileText);
    } else {
        navigator.clipboard.writeText(profileText);
        showToast('Profile info copied to clipboard!', 'success');
    }
}

// Utility functions
function showLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.classList.add('show');
}

function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.classList.remove('show');
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
    
    // Haptic feedback
    if (tg.HapticFeedback) {
        tg.HapticFeedback.notificationOccurred(type === 'error' ? 'error' : 'success');
    }
}

// Handle app lifecycle
tg.onEvent('mainButtonClicked', () => {
    // Handle main button clicks if needed
});

tg.onEvent('backButtonClicked', () => {
    // Handle back button clicks
    tg.close();
});

// Handle viewport changes
window.addEventListener('resize', () => {
    tg.expand();
});

// Export functions for global access
window.LinkUpApp = {
    switchTab,
    shareQRCode,
    downloadQRCode,
    scanQRCode,
    createGroup,
    shareProfile
}; 