// Main JavaScript for SmartLearn Chatbot

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const sendButton = document.getElementById('send-button');
    const newChatBtn = document.getElementById('new-chat');
    const breakReminderBtn = document.getElementById('break-reminder');
    const settingsBtn = document.getElementById('settings-btn');
    const helpBtn = document.getElementById('help-btn');
    const settingsModal = document.getElementById('settings-modal');
    const helpModal = document.getElementById('help-modal');
    const closeSettings = document.getElementById('close-settings');
    const closeHelp = document.getElementById('close-help');
    const settingsForm = document.getElementById('settings-form');
    const cancelSettings = document.getElementById('cancel-settings');
    const suggestionBtns = document.querySelectorAll('.suggestion-btn');
    const clearInputBtn = document.getElementById('clear-input');
    
    // State
    let isProcessing = false;
    let currentSessionId = null;
    let breakTimer = null;
    
    // Initialize the application
    function init() {
        loadPreferences();
        setupEventListeners();
        checkForReturningUser();
        setupAccessibility();
    }
    
    // Set up event listeners
    function setupEventListeners() {
        // Form submission
        chatForm.addEventListener('submit', handleSubmit);
        
        // Input handling
        userInput.addEventListener('input', handleInput);
        userInput.addEventListener('keydown', handleKeyDown);
        
        // Button clicks
        newChatBtn.addEventListener('click', startNewChat);
        breakReminderBtn.addEventListener('click', showBreakReminder);
        settingsBtn.addEventListener('click', () => toggleModal(settingsModal));
        helpBtn.addEventListener('click', () => toggleModal(helpModal));
        closeSettings.addEventListener('click', () => toggleModal(settingsModal, false));
        closeHelp.addEventListener('click', () => toggleModal(helpModal, false));
        cancelSettings.addEventListener('click', () => toggleModal(settingsModal, false));
        clearInputBtn.addEventListener('click', clearInput);
        
        // Settings form
        settingsForm.addEventListener('submit', saveSettings);
        
        // Suggestion buttons
        suggestionBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const suggestionText = btn.querySelector('.font-medium').textContent;
                userInput.value = suggestionText;
                userInput.focus();
            });
        });
        
        // Close modals when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === settingsModal) toggleModal(settingsModal, false);
            if (e.target === helpModal) toggleModal(helpModal, false);
        });
    }
    
    // Handle form submission
    async function handleSubmit(e) {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message || isProcessing) return;
        
        // Add user message to chat
        addMessage('user', message);
        clearInput();
        
        // Show typing indicator
        showTypingIndicator();
        isProcessing = true;
        
        try {
            // Create or get session ID
            if (!currentSessionId) {
                const sessionResponse = await fetch('/api/chat/sessions/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        title: message.substring(0, 30) + (message.length > 30 ? '...' : '')
                    })
                });
                
                if (!sessionResponse.ok) throw new Error('Failed to create chat session');
                
                const sessionData = await sessionResponse.json();
                currentSessionId = sessionData.id;
            }
            
            // Send message to backend
            const response = await fetch('/api/chat/messages/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    session: currentSessionId,
                    content: message,
                    is_user: true
                })
            });
            
            if (!response.ok) throw new Error('Failed to send message');
            
            // Get bot response
            const botResponse = await getBotResponse(message);
            
            // Remove typing indicator
            hideTypingIndicator();
            
            // Add bot response to chat
            addMessage('bot', botResponse);
            
            // Save bot response to backend
            await fetch('/api/chat/messages/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    session: currentSessionId,
                    content: botResponse,
                    is_user: false
                })
            });
            
            // Check for break reminder
            checkBreakReminder();
            
        } catch (error) {
            console.error('Error:', error);
            hideTypingIndicator();
            addMessage('bot', 'Sorry, I encountered an error. Please try again.');
        } finally {
            isProcessing = false;
        }
    }
    
    // Get bot response from the server
    async function getBotResponse(message) {
        try {
            const response = await fetch('/api/chat/generate-response/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    message: message,
                    session_id: currentSessionId
                })
            });
            
            if (!response.ok) throw new Error('Failed to get bot response');
            
            const data = await response.json();
            return data.response;
        } catch (error) {
            console.error('Error getting bot response:', error);
            return 'I apologize, but I encountered an issue generating a response. Could you please rephrase your question or try again later?';
        }
    }
    
    // Add a message to the chat
    function addMessage(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${sender} ${sender === 'user' ? 'user-message' : 'bot-message'}`;
        
        // Process markdown if it's a bot message
        const messageContent = sender === 'bot' ? marked.parse(content) : content;
        
        messageDiv.innerHTML = `
            <div class="message-content">${messageContent}</div>
            <div class="message-info">
                ${sender === 'user' ? 'You' : 'SmartLearn'}
                <span class="ml-2 text-xs opacity-60">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Show typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = '<span></span><span></span><span></span>';
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Hide typing indicator
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Handle input changes
    function handleInput() {
        // Auto-resize textarea
        userInput.style.height = 'auto';
        userInput.style.height = (userInput.scrollHeight) + 'px';
        
        // Toggle clear button visibility
        clearInputBtn.style.visibility = userInput.value.trim() ? 'visible' : 'hidden';
    }
    
    // Handle keyboard shortcuts
    function handleKeyDown(e) {
        // Submit on Ctrl+Enter or Cmd+Enter
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
        
        // Add new line with Shift+Enter
        if (e.key === 'Enter' && e.shiftKey) {
            e.preventDefault();
            const start = userInput.selectionStart;
            const end = userInput.selectionEnd;
            userInput.value = userInput.value.substring(0, start) + '\n' + userInput.value.substring(end);
            userInput.selectionStart = userInput.selectionEnd = start + 1;
            handleInput();
        }
    }
    
    // Clear input field
    function clearInput() {
        userInput.value = '';
        handleInput();
        userInput.focus();
    }
    
    // Start a new chat session
    function startNewChat() {
        if (confirm('Are you sure you want to start a new chat? Your current chat will be saved.')) {
            currentSessionId = null;
            chatMessages.innerHTML = '';
            addWelcomeMessage();
        }
    }
    
    // Show break reminder
    function showBreakReminder() {
        const modal = document.getElementById('break-reminder-modal');
        toggleModal(modal, true);
        
        // Start break timer
        startBreakTimer();
    }
    
    // Start break timer
    function startBreakTimer() {
        // Clear any existing timer
        if (breakTimer) clearTimeout(breakTimer);
        
        // Set timer for 5 minutes (300000 ms)
        breakTimer = setTimeout(() => {
            // Show notification
            if (Notification.permission === 'granted') {
                new Notification('Break Time!', {
                    body: 'You\'ve been working for a while. Take a short break!',
                    icon: '/static/chatbot/images/notification-icon.png'
                });
            }
            
            // Show on-screen reminder
            showBreakReminder();
        }, 300000); // 5 minutes
    }
    
    // Check if it's time for a break
    function checkBreakReminder() {
        // Simple implementation: remind every 5 messages
        const messageCount = document.querySelectorAll('.message').length;
        if (messageCount > 0 && messageCount % 5 === 0) {
            showBreakReminder();
        }
    }
    
    // Toggle modal visibility
    function toggleModal(modal, show = null) {
        if (show === null) {
            modal.classList.toggle('hidden');
        } else if (show) {
            modal.classList.remove('hidden');
        } else {
            modal.classList.add('hidden');
        }
        
        // Add/remove body class to prevent scrolling when modal is open
        if (!modal.classList.contains('hidden')) {
            document.body.classList.add('modal-open');
        } else {
            document.body.classList.remove('modal-open');
        }
    }
    
    // Save user preferences
    function saveSettings(e) {
        e.preventDefault();
        
        const formData = new FormData(settingsForm);
        const preferences = {
            highContrast: formData.get('high_contrast') === 'on',
            dyslexicFont: formData.get('dyslexic_font') === 'on',
            textToSpeech: formData.get('text_to_speech') === 'on',
            responseLength: formData.get('response_length'),
            learningStyle: formData.get('learning_style')
        };
        
        // Save to localStorage
        localStorage.setItem('smartlearn_preferences', JSON.stringify(preferences));
        
        // Apply preferences
        applyPreferences(preferences);
        
        // Close modal
        toggleModal(settingsModal, false);
        
        // Show success message
        alert('Settings saved successfully!');
    }
    
    // Load user preferences
    function loadPreferences() {
        const savedPreferences = localStorage.getItem('smartlearn_preferences');
        if (savedPreferences) {
            const preferences = JSON.parse(savedPreferences);
            
            // Update form fields
            document.getElementById('high-contrast').checked = preferences.highContrast || false;
            document.getElementById('dyslexic-font').checked = preferences.dyslexicFont || false;
            document.getElementById('text-to-speech').checked = preferences.textToSpeech || false;
            
            if (preferences.responseLength) {
                document.getElementById('response-length').value = preferences.responseLength;
            }
            
            if (preferences.learningStyle) {
                document.getElementById('learning-style').value = preferences.learningStyle;
            }
            
            // Apply preferences
            applyPreferences(preferences);
        }
    }
    
    // Apply accessibility preferences
    function applyPreferences(preferences) {
        const body = document.body;
        
        // High contrast mode
        if (preferences.highContrast) {
            body.classList.add('high-contrast');
        } else {
            body.classList.remove('high-contrast');
        }
        
        // Dyslexic font
        if (preferences.dyslexicFont) {
            body.classList.add('dyslexic-font');
        } else {
            body.classList.remove('dyslexic-font');
        }
        
        // Text-to-speech
        if (preferences.textToSpeech && 'speechSynthesis' in window) {
            // Enable text-to-speech
            setupTextToSpeech();
        }
    }
    
    // Setup text-to-speech functionality
    function setupTextToSpeech() {
        if ('speechSynthesis' in window) {
            // Add event listener to read bot messages
            chatMessages.addEventListener('click', (e) => {
                const messageContent = e.target.closest('.message-bot')?.querySelector('.message-content');
                if (messageContent) {
                    const text = messageContent.textContent;
                    const utterance = new SpeechSynthesisUtterance(text);
                    speechSynthesis.speak(utterance);
                }
            });
        }
    }
    
    // Check if user is returning
    function checkForReturningUser() {
        const lastVisit = localStorage.getItem('last_visit');
        const now = new Date().toISOString();
        
        if (lastVisit) {
            // Show welcome back message if it's been more than a day
            const lastVisitDate = new Date(lastVisit);
            const daysSinceLastVisit = Math.floor((new Date(now) - lastVisitDate) / (1000 * 60 * 60 * 24));
            
            if (daysSinceLastVisit > 0) {
                addMessage('bot', `Welcome back! It's been ${daysSinceLastVisit} day${daysSinceLastVisit > 1 ? 's' : ''} since your last visit.`);
            }
        } else {
            // First-time user
            addWelcomeMessage();
        }
        
        // Update last visit time
        localStorage.setItem('last_visit', now);
    }
    
    // Add welcome message
    function addWelcomeMessage() {
        const welcomeMessage = `Hello! I'm your SmartLearn assistant. I can help you with:
        
- Explaining complex concepts in simple terms
- Answering your questions on various topics
- Providing study tips and techniques
- Breaking down problems step by step
- And much more!

How can I help you today?`;
        
        addMessage('bot', welcomeMessage);
    }
    
    // Setup accessibility features
    function setupAccessibility() {
        // Request notification permission
        if ('Notification' in window && Notification.permission !== 'denied') {
            Notification.requestPermission();
        }
        
        // Add keyboard navigation
        document.addEventListener('keydown', (e) => {
            // Focus trap for modals
            if (document.body.classList.contains('modal-open')) {
                const activeElement = document.activeElement;
                const focusableElements = Array.from(document.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'));
                const firstElement = focusableElements[0];
                const lastElement = focusableElements[focusableElements.length - 1];
                
                if (e.key === 'Tab') {
                    if (e.shiftKey && activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    } else if (!e.shiftKey && activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                } else if (e.key === 'Escape') {
                    const openModal = document.querySelector('.modal:not(.hidden)');
                    if (openModal) {
                        toggleModal(openModal, false);
                    }
                }
            }
        });
    }
    
    // Get CSRF token from cookies
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }
    
    // Initialize the app
    init();
});
