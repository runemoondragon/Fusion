let currentImageData = null;
let currentMediaType = null;
let selectedMode = null;

// Auto-resize textarea
const textarea = document.getElementById('message-input');
textarea.addEventListener('input', function() {
    this.style.height = '28px';
    this.style.height = (this.scrollHeight) + 'px';
});

// Function to get the current provider's avatar path
function getProviderAvatarPath(providerName) {
    // Return null for NeuroSwitch, handle it separately
    if (!providerName || providerName.toLowerCase() === 'neuroswitch') {
        return null;
    }
    switch (providerName.toLowerCase()) {
        case 'claude':
            return '/static/claude.png';
        case 'openai':
            return '/static/openai.png';
        case 'gemini':
            return '/static/gemini.png';
        default:
            return null; // Default case
    }
}

// --- UPDATED: appendMessage to explicitly use the provider argument for AI messages ---
function appendMessage(content, sender = 'ai', provider = 'claude', toolName = null, isThinking = false) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'message-wrapper';
    if (isThinking) {
        messageWrapper.id = 'thinking-indicator'; // Add ID for easy removal
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex items-start space-x-4 space-y-1';

    // Avatar
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-xs overflow-hidden';

    if (sender === 'user') {
        avatarDiv.classList.add('bg-gray-200', 'text-gray-600');
        avatarDiv.textContent = 'You';
    } else { // AI or Thinking message
        avatarDiv.classList.add('ai-avatar');
        avatarDiv.textContent = '';

        // Determine avatar based on provider *passed to this function*
        const avatarPath = getProviderAvatarPath(provider);
        console.log(`[appendMessage ${isThinking ? '(Thinking)' : '(Final)'}] Provider='${provider}', Path='${avatarPath}'`);

        if (avatarPath) {
            const img = document.createElement('img');
            img.src = avatarPath;
            img.alt = `${provider} avatar`;
            img.className = 'w-full h-full object-cover';
            avatarDiv.appendChild(img);
        } else {
            // Fallback: Use first 2 letters or 'NE' for NeuroSwitch default
            avatarDiv.textContent = provider.toLowerCase() === 'neuroswitch' ? 'NE' : provider.substring(0, 2).toUpperCase();
             avatarDiv.classList.add('bg-gray-400'); // Add a background for text avatars
        }
    }

    // Message content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'flex-1';

    if (isThinking) {
        const thinkingDiv = document.createElement('div');
        thinkingDiv.className = 'thinking';
        thinkingDiv.innerHTML = '<div style="margin-top: 6px; margin-bottom: 4px;">Thinking<span class="thinking-dots"><span>.</span><span>.</span><span>.</span></span></div>';
        contentDiv.appendChild(thinkingDiv);
    } else {
        const innerDiv = document.createElement('div');
        innerDiv.className = 'prose prose-slate max-w-none';
        if (sender === 'ai' && content) {
            try {
                innerDiv.innerHTML = marked.parse(content);
                // Apply syntax highlighting after parsing
                innerDiv.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });
            } catch (e) {
                console.error('Error parsing markdown:', e);
                innerDiv.textContent = content;
            }
        } else {
            innerDiv.textContent = content || '';
        }
        contentDiv.appendChild(innerDiv);

        // Add tool usage indicator if toolName is provided
        if (toolName) {
            const toolDiv = document.createElement('div');
            toolDiv.className = 'text-xs text-gray-500 mt-1';
            toolDiv.textContent = `🔩 Used tool: ${toolName}`;
            contentDiv.appendChild(toolDiv);
        }
    }

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    messageWrapper.appendChild(messageDiv);
    messagesDiv.appendChild(messageWrapper);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Event Listeners
document.getElementById('upload-btn').addEventListener('click', () => {
    document.getElementById('file-input').click();
});

document.getElementById('file-input').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (data.success) {
                currentImageData = data.image_data;
                currentMediaType = data.media_type;
                document.getElementById('preview-img').src = `data:${data.media_type};base64,${data.image_data}`;
                document.getElementById('image-preview').classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error uploading image:', error);
        }
    }
});

document.getElementById('remove-image').addEventListener('click', () => {
    currentImageData = null;
    document.getElementById('image-preview').classList.add('hidden');
    document.getElementById('file-input').value = '';
});

// --- UPDATED: Function to update the token usage bar ---
function updateTokenUsage(usageData) { // Accept the whole usage object
    const maxTokensDefault = 200000; // Use a default if max_tokens isn't provided
    
    // Extract values, providing defaults if missing or invalid
    const usedTokens = parseInt(usageData?.total_tokens) || 0;
    const maxTokens = parseInt(usageData?.max_tokens) || maxTokensDefault;
    
    // Calculate percentage, handle potential division by zero
    const percentage = maxTokens > 0 ? (usedTokens / maxTokens) * 100 : 0;
    
    const tokenBar = document.getElementById('token-bar');
    const tokensUsedSpan = document.getElementById('tokens-used'); // Renamed variable for clarity
    const maxTokensSpan = document.getElementById('max-tokens'); // Get the max tokens span
    const tokenPercentageSpan = document.getElementById('token-percentage'); // Renamed variable
    
    // Ensure elements exist before updating
    if (tokenBar && tokensUsedSpan && maxTokensSpan && tokenPercentageSpan) {
        // Update the numbers
        tokensUsedSpan.textContent = usedTokens.toLocaleString();
        maxTokensSpan.textContent = maxTokens.toLocaleString(); // Update max tokens display
        tokenPercentageSpan.textContent = `${percentage.toFixed(1)}%`;
        
        // Update the bar width
        tokenBar.style.width = `${Math.min(percentage, 100)}%`; // Cap width at 100%
        
        // Update colors based on usage
        tokenBar.classList.remove('warning', 'danger');
        if (percentage > 90) {
            tokenBar.classList.add('danger');
        } else if (percentage > 75) {
            tokenBar.classList.add('warning');
        }
    } else {
        console.error("Token usage UI elements not found!");
    }
}

// Function to handle sending chat messages
async function sendChatMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    const currentImage = currentImageData;
    const currentMode = selectedMode;

    if (!message && !currentImage) return;

    // ** Hide welcome message and suggestions **
    document.getElementById('welcome-message')?.classList.add('hidden');
    document.getElementById('suggestion-cards-row')?.classList.add('hidden');

    // Append user message
    appendMessage(message, 'user'); // Sender is user
    // Optional: Display user-uploaded image inline (needs modification in appendMessage)

    // Clear input and reset height, clear image preview
    messageInput.value = '';
    resetTextarea();
    currentImageData = null; // Clear global state after capturing
    currentMediaType = null;
    selectedMode = null;
    document.getElementById('image-preview').classList.add('hidden');
    document.getElementById('file-input').value = '';
    document.querySelectorAll('.feature-button.active').forEach(btn => btn.classList.remove('active'));

    // --- Show thinking indicator with appropriate avatar --- 
    const providerSelect = document.getElementById('provider-select');
    const initialProviderSelection = providerSelect ? providerSelect.value : 'claude';
    appendMessage('', 'ai', initialProviderSelection, null, true); // Pass selected provider, isThinking=true

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                image: currentImage,
                mode: currentMode
            })
        });

        // Remove thinking indicator
        const thinkingMessage = document.getElementById('thinking-indicator');
        if (thinkingMessage) thinkingMessage.remove();

        // --- Handle response (including errors) --- 
        let data = {};
        try {
             data = await response.json();
        } catch (parseError) {
            console.error("Failed to parse JSON response:", parseError);
            // Synthesize error data structure
            data = {
                response: "Server returned invalid data.",
                provider_used: initialProviderSelection, // Guess provider
                neuroswitch_active: false,
                fallback_reason: "Invalid server response",
                token_usage: {}
            };
            if (!response.ok) {
                 data.response = `Server error (${response.status}). Could not parse response.`;
            }
        }

        console.log('Chat response data:', data); // Log for debugging
        
        // Extract data, providing defaults
        const providerUsed = data.provider_used || initialProviderSelection; // Use actual or initial
        const isNeuroSwitchActive = data.neuroswitch_active === true;
        const fallbackReason = data.fallback_reason;
        const responseText = data.response || (response.ok ? "[No response text]" : "Error retrieving response");
        const toolName = data.tool_name;
        const tokenUsage = data.token_usage || {}; // Ensure tokenUsage is an object

        // Append the actual AI response using providerUsed
        appendMessage(responseText, 'ai', providerUsed, toolName, false);

        // Update token usage bar
        if (tokenUsage.total_tokens !== undefined) { updateTokenUsage(tokenUsage); }

        // Update NeuroSwitch indicator based on response
        updateNeuroSwitchIndicator(isNeuroSwitchActive, fallbackReason);

    } catch (error) {
        console.error('Chat fetch error:', error);
        // Remove thinking indicator if it exists on error
        document.getElementById('thinking-indicator')?.remove();
        // Display error message (maybe use initial selection for avatar?)
        appendMessage(`Error sending message: ${error.message}`, 'ai', initialProviderSelection);
         // Update indicator on fetch error
         updateNeuroSwitchIndicator(false, 'Network Error');
    }
}

function resetTextarea() {
    const textarea = document.getElementById('message-input');
    textarea.style.height = '28px';
}

document.getElementById('chat-form').addEventListener('reset', () => {
    resetTextarea();
});

// Add at the top of the file
window.addEventListener('load', async () => {
    try {
        // Reset the conversation when page loads
        const response = await fetch('/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            console.error('Failed to reset conversation');
        }
        
        // Clear any existing messages except the first one
        const messagesDiv = document.getElementById('chat-messages');
        const messages = messagesDiv.getElementsByClassName('message-wrapper');
        while (messages.length > 1) {
            messages[1].remove();
        }
        
        // Reset any other state
        currentImageData = null;
        document.getElementById('image-preview')?.classList.add('hidden');
        document.getElementById('file-input').value = '';
        document.getElementById('message-input').value = '';
        resetTextarea();
        
        // Reset token usage display
        updateTokenUsage({ total_tokens: 0, max_tokens: 200000 });

        // ** Show welcome message and suggestions on reset **
        document.getElementById('welcome-message')?.classList.remove('hidden');
        document.getElementById('suggestion-cards-row')?.classList.remove('hidden');

        // Set initial NeuroSwitch indicator state
        updateNeuroSwitchIndicator(false, null);
        // Adjust token bar on load
        adjustTokenBarPosition();

    } catch (error) {
        console.error('Error resetting conversation:', error);
    }
});

// --- ADDED: Function to update NeuroSwitch status indicator ---
function updateNeuroSwitchIndicator(isActive, reason = null) {
    const statusIndicator = document.getElementById('neuroswitch-status-indicator');
    const providerSelect = document.getElementById('provider-select');
    if (!statusIndicator || !providerSelect) return; // Elements not found

    const currentSelection = providerSelect.value;

    if (currentSelection === 'NeuroSwitch') {
        if (isActive) {
            statusIndicator.innerHTML = '✅'; // Simple checkmark for active
            statusIndicator.className = 'ml-2 text-xs text-green-600';
            statusIndicator.title = 'NeuroSwitch Active';
        } else if (reason) {
            statusIndicator.innerHTML = '⚠️'; // Warning sign for fallback
            statusIndicator.className = 'ml-2 text-xs text-yellow-600';
            statusIndicator.title = `NeuroSwitch Fallback: ${reason}`; // Set title for hover
        } else {
            // NeuroSwitch selected but no status yet (e.g., before first message)
            statusIndicator.innerHTML = '⚙️'; // Gear icon or similar
            statusIndicator.className = 'ml-2 text-xs text-gray-500';
            statusIndicator.title = 'NeuroSwitch Ready';
        }
    } else {
        // Clear indicator if NeuroSwitch is not selected
        statusIndicator.innerHTML = '';
        statusIndicator.title = '';
    }
}

// Auto-resize textarea
// ... (textarea resize logic) ...

// Handle Cmd/Ctrl + Enter for sending
// ... (keypress listener logic) ...

// Image upload handling
// ... (upload button, file input, preview logic) ...

// Provider selection change handling
const providerSelect = document.getElementById('provider-select');
if (providerSelect) {
    providerSelect.addEventListener('change', async (event) => {
        const selectedProvider = event.target.value;
        console.log(`Selected provider: ${selectedProvider}`);
        // --- Update indicator immediately on change --- 
        if (selectedProvider === 'NeuroSwitch') {
            // Set to 'Ready' state initially when selected
            updateNeuroSwitchIndicator(false, null); 
        } else {
            // Clear indicator if switching away from NeuroSwitch
            updateNeuroSwitchIndicator(false, null);
        }
        
        try {
            const response = await fetch('/set_provider', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ provider: selectedProvider })
            });
            const data = await response.json();
            if (data.status === 'success') {
                console.log('Provider updated successfully on server.');
            } else {
                console.error('Failed to update provider on server:', data.message);
                 // Optionally revert selection or show error?
            }
        } catch (error) {
            console.error('Error setting provider:', error);
        }
    });
    // --- Initial indicator state on load --- 
    updateNeuroSwitchIndicator(false, null); // Set initial state based on loaded selection
}

// Adjust token bar position dynamically
// ... (adjustTokenBarPosition and observer logic) ...

// Suggestion card click handling
// ... (suggestion card listener logic) ... 

// --- Helper Functions (Moved from index.html) ---

// Function to adjust token bar position based on input area height dynamically
function adjustTokenBarPosition() {
    const inputWrapper = document.querySelector('.input-wrapper');
    const tokenContainer = document.querySelector('.token-usage-container');
    if (inputWrapper && tokenContainer) {
        const inputHeight = inputWrapper.offsetHeight;
        tokenContainer.style.bottom = `${inputHeight}px`;
    }
}

function resetTextarea() {
    const textarea = document.getElementById('message-input');
    if (textarea) { // Check if element exists
        textarea.style.height = '40px'; // Reset to initial computed height or a fixed value
        textarea.value = ''; // Also clear value on reset
    }
}

// --- Main Chat Logic ---

// Function to handle sending chat messages
async function sendChatMessage() {
    // ... (sendChatMessage function remains largely the same as the last version) ...
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    const currentImage = currentImageData; // Capture image data

    if (!message && !currentImage) return;

    document.getElementById('welcome-message')?.classList.add('hidden');
    document.getElementById('suggestion-cards-row')?.classList.add('hidden');

    appendMessage(message, 'user');

    // Clear input/image AFTER capturing data
    resetTextarea(); // Resets height and clears value
    currentImageData = null;
    currentMediaType = null;
    selectedMode = null;
    document.getElementById('image-preview').classList.add('hidden');
    document.getElementById('file-input').value = '';

    const providerSelect = document.getElementById('provider-select');
    const initialProviderSelection = providerSelect ? providerSelect.value : 'claude';
    appendMessage('', 'ai', initialProviderSelection, null, true); // Thinking indicator

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message, image: currentImage })
        });

        document.getElementById('thinking-indicator')?.remove();

        let data = {};
        try {
            data = await response.json();
        } catch (parseError) {
            console.error("Failed to parse JSON response:", parseError);
            data = { /* ... synthesize error data ... */ };
             data.response = `Server error (${response.status || 'unknown'}). Could not parse response.`;
             data.provider_used = initialProviderSelection;
             data.neuroswitch_active = false;
             data.fallback_reason = "Invalid server response";
             data.token_usage = {};
        }

        console.log('Chat response data:', data); // Log for debugging

        const providerUsed = data.provider_used || initialProviderSelection;
        const isNeuroSwitchActive = data.neuroswitch_active === true;
        const fallbackReason = data.fallback_reason;
        const responseText = data.response || (response.ok ? "[No response text]" : "Error retrieving response");
        const toolName = data.tool_name;
        const tokenUsage = data.token_usage || {};

        // Append final response
        appendMessage(responseText, 'ai', providerUsed, toolName, false);

        if (tokenUsage.total_tokens !== undefined) { updateTokenUsage(tokenUsage); }

        updateNeuroSwitchIndicator(isNeuroSwitchActive, fallbackReason);

    } catch (error) {
        console.error('Chat fetch error:', error);
        document.getElementById('thinking-indicator')?.remove();
        appendMessage(`Error sending message: ${error.message}`, 'ai', initialProviderSelection);
        updateNeuroSwitchIndicator(false, 'Network Error');
    }
}

// --- Event Listeners Initialization ---

// Use DOMContentLoaded to ensure elements are ready before attaching listeners
document.addEventListener('DOMContentLoaded', () => {

    // --- Chat Form Submission ---
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            sendChatMessage();
        });
        // Add reset handler if needed (though page load handles reset now)
        // chatForm.addEventListener('reset', resetTextarea);
    }

    // --- Auto-resize Textarea ---
    const messageInput = document.getElementById('message-input');
    if (messageInput) {
        messageInput.addEventListener('input', function() {
            this.style.height = '40px'; // Reset height first
            this.style.height = Math.max(40, this.scrollHeight) + 'px'; // Use scrollHeight, min 40px
             adjustTokenBarPosition(); // Adjust token bar when textarea resizes
        });

        // --- Cmd/Ctrl + Enter Handler ---
        messageInput.addEventListener('keydown', (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
                e.preventDefault();
                chatForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
            }
        });
    }

    // --- Image Upload Handling ---
    const uploadBtn = document.getElementById('upload-btn');
    const fileInput = document.getElementById('file-input');
    const removeImageBtn = document.getElementById('remove-image');
    const imagePreviewDiv = document.getElementById('image-preview');
    const previewImg = document.getElementById('preview-img');

    if (uploadBtn) {
        uploadBtn.addEventListener('click', () => fileInput?.click());
    }

    if (fileInput) {
        fileInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (file && imagePreviewDiv && previewImg) {
                // ... (existing image upload fetch logic) ...
                 try {
                     const formData = new FormData();
                     formData.append('file', file);
                     const response = await fetch('/upload', { method: 'POST', body: formData });
                     const data = await response.json();
                     if (data.success) {
                         currentImageData = data.image_data;
                         currentMediaType = data.media_type;
                         previewImg.src = `data:${data.media_type};base64,${data.image_data}`;
                         imagePreviewDiv.classList.remove('hidden');
                         adjustTokenBarPosition(); // Adjust token bar after image preview shown
                     } else {
                         console.error("Upload failed:", data.error);
                         // TODO: Show error to user
                     }
                 } catch (error) {
                     console.error('Error uploading image:', error);
                 }
            }
        });
    }

    if (removeImageBtn) {
        removeImageBtn.addEventListener('click', () => {
            currentImageData = null;
            currentMediaType = null;
            if (imagePreviewDiv) imagePreviewDiv.classList.add('hidden');
            if (fileInput) fileInput.value = '';
            adjustTokenBarPosition(); // Adjust token bar after image preview hidden
        });
    }

    // --- Provider Selection Handling (Moved from index.html) ---
    const providerSelect = document.getElementById('provider-select'); // Declare here
    if (providerSelect) {
        providerSelect.addEventListener('change', async (event) => {
            const selectedProvider = event.target.value;
            console.log(`Selected provider: ${selectedProvider}`);

            // Update indicator immediately on change
            updateNeuroSwitchIndicator(false, null); // Will clear or set to ready (⚙️)

            try {
                const response = await fetch('/set_provider', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ provider: selectedProvider })
                });
                const data = await response.json();
                if (data.status === 'success') {
                    console.log('Provider updated successfully on server.');
                } else {
                    console.error('Failed to update provider on server:', data.message);
                }
            } catch (error) {
                console.error('Error setting provider:', error);
            }
        });
        // --- Initial indicator state on load --- 
        updateNeuroSwitchIndicator(false, null); // Set initial state based on loaded selection
    }

    // --- Token Bar Position Adjustment (Moved from index.html) ---
    window.addEventListener('resize', adjustTokenBarPosition);
    // Initial adjustment might be needed if elements load sized differently
    adjustTokenBarPosition();

    // Observer for input wrapper size changes (e.g., image preview)
    const inputWrapper = document.querySelector('.input-wrapper');
    if (inputWrapper) {
        const observer = new MutationObserver(adjustTokenBarPosition);
        observer.observe(inputWrapper, { childList: true, subtree: true, attributes: true });
    }

    // --- Suggestion Card Click Handling (Moved from index.html) ---
    document.querySelectorAll('.suggestion-card .tag').forEach(tag => {
        // Make only command tags clickable
        if (tag.textContent !== 'Available commands') {
             tag.style.cursor = 'pointer';
             tag.addEventListener('click', () => {
                 const command = tag.textContent;
                 const messageInput = document.getElementById('message-input');
                 if (messageInput) {
                     messageInput.value = command;
                     messageInput.focus();
                     // Trigger input event for auto-resize and adjust token bar
                     messageInput.dispatchEvent(new Event('input', { bubbles: true }));
                 }
             });
        }
    });

    // --- ADDED: Mode Button Handling ---
    const featureButtons = document.querySelectorAll('.feature-button[data-mode]');
    featureButtons.forEach(button => {
        button.addEventListener('click', () => {
            const mode = button.dataset.mode;
            // Remove active class from all buttons
            featureButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to the clicked button
            button.classList.add('active');
            // Store the selected mode
            selectedMode = mode;
            console.log(`Selected mode: ${selectedMode}`);
            // Optional: Maybe focus input or provide other feedback
        });
    });

    // --- Initial Page Load Reset Logic ---
    // Using a flag to prevent multiple resets if script reloads with debug mode
    if (!window.pageHasLoaded) {
        window.pageHasLoaded = true; // Set flag
        fetch('/reset', { method: 'POST' })
            .then(response => {
                if (!response.ok) console.error('Initial reset failed');
                else console.log('Initial conversation reset successful.');
                // Reset token display after successful reset
                updateTokenUsage({ total_tokens: 0, max_tokens: 200000 }); // Pass object
            })
            .catch(error => console.error('Error during initial reset:', error));
            
         // Ensure welcome message is visible on initial load
         document.getElementById('welcome-message')?.classList.remove('hidden');
         document.getElementById('suggestion-cards-row')?.classList.remove('hidden');
    }

}); // End DOMContentLoaded 