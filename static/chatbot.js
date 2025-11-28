// Chatbot functionality
function toggleChat() {
    const popup = document.getElementById('chatPopup');
    popup.classList.toggle('active');
    if (popup.classList.contains('active')) {
        document.getElementById('chatUserInput').focus();
    }
}

function sendMessage(event) {
    event.preventDefault();
    const input = document.getElementById('chatUserInput');
    const message = input.value.trim();
    
    if (!message) return;

    const messagesContainer = document.getElementById('chatMessages');
    
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'message user';
    userMessageDiv.innerHTML = `
        <span class="message-label">You</span>
        <div class="message-bubble">${escapeHtml(message)}</div>
    `;
    messagesContainer.appendChild(userMessageDiv);
    
    input.value = '';
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    fetch(`https://jaidel-chestnut-portfolio.onrender.com/get?msg=${encodeURIComponent(message)}`)
        .then(response => response.text())
        .then(data => {
            const botMessageDiv = document.createElement('div');
            botMessageDiv.className = 'message bot';
            botMessageDiv.innerHTML = `
                <span class="message-label">Bot</span>
                <div class="message-bubble">${escapeHtml(data)}</div>
            `;
            messagesContainer.appendChild(botMessageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        })
        .catch(error => {
            console.error('Error:', error);
            const errorDiv = document.createElement('div');
            errorDiv.className = 'message bot';
            errorDiv.innerHTML = `
                <span class="message-label">Bot</span>
                <div class="message-bubble">Sorry, I encountered an error. Please try again.</div>
            `;
            messagesContainer.appendChild(errorDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}


