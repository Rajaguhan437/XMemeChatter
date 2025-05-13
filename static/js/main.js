document.addEventListener('DOMContentLoaded', function() {
    // Initialize Feather icons
    feather.replace();
    
    // Enable tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Function to update progress bar for active session
    function updateProgress() {
        // Only run if automation is active
        const statusElement = document.querySelector('.card.bg-success');
        if (!statusElement) return;
        
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                if (data.is_running && data.active_session) {
                    const progressBar = document.querySelector('.progress-bar');
                    if (progressBar) {
                        const session = data.active_session;
                        const percent = (session.comments_processed / session.comments_target) * 100;
                        
                        progressBar.style.width = `${percent}%`;
                        progressBar.setAttribute('aria-valuenow', session.comments_processed);
                        progressBar.textContent = `${session.comments_processed}/${session.comments_target}`;
                        
                        // If session is complete, refresh the page
                        if (session.comments_processed >= session.comments_target) {
                            setTimeout(() => {
                                window.location.reload();
                            }, 2000);
                        }
                    }
                }
            })
            .catch(error => console.error('Error updating status:', error));
    }
    
    // Check status every 5 seconds if automation is running
    if (document.querySelector('.card.bg-success')) {
        setInterval(updateProgress, 5000);
    }
    
    // Password visibility toggle
    const passwordToggle = document.querySelector('.password-toggle');
    if (passwordToggle) {
        passwordToggle.addEventListener('click', function() {
            const passwordField = document.querySelector('#x_password');
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);
            
            // Toggle icon
            const icon = this.querySelector('i');
            if (type === 'text') {
                icon.classList.remove('bi-eye');
                icon.classList.add('bi-eye-slash');
            } else {
                icon.classList.remove('bi-eye-slash');
                icon.classList.add('bi-eye');
            }
        });
    }
    
    // AI provider change handler
    const aiProviderSelect = document.querySelector('#ai_provider');
    if (aiProviderSelect) {
        aiProviderSelect.addEventListener('change', function() {
            const selectedProvider = this.value;
            const chatgptFields = document.querySelector('#chatgpt_fields');
            const xaiFields = document.querySelector('#xai_fields');
            
            if (selectedProvider === 'chatgpt') {
                chatgptFields.classList.remove('d-none');
                if (xaiFields) xaiFields.classList.add('d-none');
            } else {
                if (chatgptFields) chatgptFields.classList.add('d-none');
                if (xaiFields) xaiFields.classList.remove('d-none');
            }
        });
    }
    
    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            const alert = new bootstrap.Alert(message);
            alert.close();
        }, 5000);
    });
});
