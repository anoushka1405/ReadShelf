document.addEventListener('DOMContentLoaded', () => {
    const chatWindow = document.getElementById('chat-window');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
  
    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();  // Prevent form submission page reload
  
      const message = chatInput.value.trim();
      if (!message) return;
  
      // Add user message
      chatWindow.innerHTML += `<p class="user-message"><strong>You:</strong> ${message}</p>`;
  
      // Scroll to bottom
      chatWindow.scrollTop = chatWindow.scrollHeight;
  
      // Add typing indicator
      chatWindow.innerHTML += `<p class="bot-message typing"><strong>Bot:</strong> Typing...</p>`;
      chatWindow.scrollTop = chatWindow.scrollHeight;
  
      try {
        const response = await fetch('/readbot', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message }),
        });
  
        const data = await response.json();
  
        // Remove typing indicator
        const typingElem = chatWindow.querySelector('.typing');
        if (typingElem) typingElem.remove();
  
        // Add bot reply
        chatWindow.innerHTML += `<p class="bot-message"><strong>Bot:</strong> ${data.reply}</p>`;
  
        chatWindow.scrollTop = chatWindow.scrollHeight;
  
        chatInput.value = '';
        chatInput.focus();
      } catch (error) {
        // Remove typing indicator if present
        const typingElem = chatWindow.querySelector('.typing');
        if (typingElem) typingElem.remove();
  
        chatWindow.innerHTML += `<p class="bot-message" style="color:red;"><strong>Bot:</strong> Sorry, something went wrong.</p>`;
        chatInput.value = '';
        chatInput.focus();
      }
    });
  });
  