/**
 * Ujval Thakor - Portfolio AI Chatbot Controller
 * Native Douglus Neo-Grotesque Assistant
 */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', initPortfolioChatbot);

  function initPortfolioChatbot() {
    const root = document.getElementById('portfolio-chatbot-root');
    const trigger = document.getElementById('chatbot-trigger');
    const chatWindow = document.getElementById('chatbot-window');
    const closeBtn = document.getElementById('chatbot-close-btn');
    const clearBtn = document.getElementById('chatbot-clear-btn');
    const form = document.getElementById('chatbot-form');
    const input = document.getElementById('chatbot-input');
    const sendBtn = document.getElementById('chatbot-send-btn');
    const messagesContainer = document.getElementById('chatbot-messages');
    const typingIndicator = document.getElementById('chatbot-typing');
    const suggestionsContainer = document.getElementById('chatbot-suggestions');

    if (!trigger || !chatWindow || !form || !input) return;

    let isRequestPending = false;
    const csrfToken = root ? root.getAttribute('data-csrf') : getCookie('csrftoken');

    // 1. Toggle Open / Close
    function toggleChat(openState) {
      const willOpen = typeof openState === 'boolean' ? openState : !chatWindow.classList.contains('is-open');

      if (willOpen) {
        chatWindow.classList.add('is-open');
        trigger.classList.add('is-active');
        trigger.setAttribute('aria-expanded', 'true');
        chatWindow.setAttribute('aria-hidden', 'false');
        
        // Auto-focus input on non-touch devices
        if (window.innerWidth > 640) {
          setTimeout(() => input.focus(), 150);
        }
        scrollToBottom();
      } else {
        chatWindow.classList.remove('is-open');
        trigger.classList.remove('is-active');
        trigger.setAttribute('aria-expanded', 'false');
        chatWindow.setAttribute('aria-hidden', 'true');
        trigger.focus();
      }
    }

    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleChat();
    });

    closeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleChat(false);
    });

    // 2. Global Shortcuts: Escape to close, Cmd+K / Ctrl+K to toggle
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && chatWindow.classList.contains('is-open')) {
        toggleChat(false);
      }
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        toggleChat();
      }
    });

    // 3. Clear Chat History
    clearBtn.addEventListener('click', async () => {
      if (isRequestPending) return;
      
      try {
        await fetch('/chatbot/api/clear/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          }
        });

        // Reset UI messages
        messagesContainer.innerHTML = `
          <div class="chat-message chat-message--assistant">
            <div class="chat-bubble">
              <p>Conversation history has been reset.</p>
              <p style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--chatbot-text-muted);">
                Ask me anything about Ujval's backend architectures, projects, technologies, or how to contact him.
              </p>
            </div>
            <span class="chat-time">Just now</span>
          </div>
        `;
        renderInitialSuggestions();
      } catch (err) {
        console.error('Failed to clear chat:', err);
      }
    });

    // 4. Handle Suggestion Click
    function setupSuggestionListeners() {
      const chips = document.querySelectorAll('.suggestion-chip');
      chips.forEach((chip) => {
        chip.onclick = () => {
          const query = chip.getAttribute('data-query');
          if (query && !isRequestPending) {
            input.value = query;
            submitMessage(query);
          }
        };
      });
    }
    setupSuggestionListeners();

    // 5. Submit Message Handler
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const message = input.value.trim();
      if (!message || isRequestPending) return;
      submitMessage(message);
    });

    async function submitMessage(userText) {
      isRequestPending = true;
      sendBtn.disabled = true;
      input.value = '';

      // Append User Bubble to DOM
      appendUserMessage(userText);
      showTyping(true);
      scrollToBottom();

      try {
        const response = await fetch('/chatbot/api/message/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
          body: JSON.stringify({ message: userText }),
        });

        showTyping(false);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        const reply = data.reply || "I apologize, but I could not generate a response. Please try again.";
        const suggestions = data.suggestions || [];

        appendAssistantMessage(reply, suggestions);
      } catch (err) {
        showTyping(false);
        console.error('Chatbot error:', err);
        appendAssistantMessage(
          "Sorry, I am having trouble responding right now. Please try asking again in a moment, or reach out to Ujval directly on the [Contact Page](/contact/) or via email at **[ujvalthakor14@gmail.com](mailto:ujvalthakor14@gmail.com)**.",
          ["How can I contact Ujval?", "View selected projects", "View resume"]
        );
      } finally {
        isRequestPending = false;
        sendBtn.disabled = false;
        scrollToBottom();
        if (window.innerWidth > 640) {
          input.focus();
        }
      }
    }

    // 6. DOM Helpers for Messages
    function appendUserMessage(text) {
      // Remove any loose suggestions from previous turn
      const prevSuggestions = document.getElementById('chatbot-suggestions');
      if (prevSuggestions) prevSuggestions.remove();

      const timeStr = getCurrentTime();
      const msgDiv = document.createElement('div');
      msgDiv.className = 'chat-message chat-message--user';
      msgDiv.innerHTML = `
        <div class="chat-bubble">
          <p>${escapeHtml(text)}</p>
        </div>
        <span class="chat-time">${timeStr}</span>
      `;
      messagesContainer.appendChild(msgDiv);
    }

    function appendAssistantMessage(markdownText, suggestions) {
      const timeStr = getCurrentTime();
      const msgDiv = document.createElement('div');
      msgDiv.className = 'chat-message chat-message--assistant';

      const formattedHtml = parseMarkdown(markdownText);
      const rawTextForCopy = markdownText.replace(/\[(.*?)\]\(.*?\)/g, '$1');

      msgDiv.innerHTML = `
        <div class="chat-bubble">
          ${formattedHtml}
        </div>
        <div class="chat-time">
          <span>${timeStr}</span>
          <span>&bull;</span>
          <button type="button" class="chat-copy-btn" title="Copy answer to clipboard">Copy</button>
        </div>
      `;

      // Copy Action
      const copyBtn = msgDiv.querySelector('.chat-copy-btn');
      if (copyBtn) {
        copyBtn.addEventListener('click', () => {
          navigator.clipboard.writeText(rawTextForCopy).then(() => {
            copyBtn.textContent = 'Copied! ✓';
            setTimeout(() => {
              copyBtn.textContent = 'Copy';
            }, 1800);
          }).catch(() => {
            copyBtn.textContent = 'Copied';
          });
        });
      }

      messagesContainer.appendChild(msgDiv);

      // Append follow-up suggestions if available
      if (suggestions && suggestions.length > 0) {
        const suggDiv = document.createElement('div');
        suggDiv.id = 'chatbot-suggestions';
        suggDiv.className = 'chatbot-suggestions';
        suggDiv.innerHTML = `
          <span class="suggestions-label">// SUGGESTED INQUIRIES:</span>
          <div class="suggestions-pills">
            ${suggestions.map(s => `<button type="button" class="suggestion-chip" data-query="${escapeHtml(s)}">${escapeHtml(s)}</button>`).join('')}
          </div>
        `;
        messagesContainer.appendChild(suggDiv);
        setupSuggestionListeners();
      }
    }

    function renderInitialSuggestions() {
      const suggDiv = document.createElement('div');
      suggDiv.id = 'chatbot-suggestions';
      suggDiv.className = 'chatbot-suggestions';
      suggDiv.innerHTML = `
        <span class="suggestions-label">// SUGGESTED INQUIRIES:</span>
        <div class="suggestions-pills">
          <button type="button" class="suggestion-chip" data-query="What backend technologies does Ujval specialize in?">Core Tech Stack</button>
          <button type="button" class="suggestion-chip" data-query="Tell me about the BeautyCare AI project">BeautyCare AI Case Study</button>
          <button type="button" class="suggestion-chip" data-query="What is Ujval's practical experience?">Engineering Experience</button>
          <button type="button" class="suggestion-chip" data-query="How can I contact or hire Ujval?">Get in Touch / Hire</button>
        </div>
      `;
      messagesContainer.appendChild(suggDiv);
      setupSuggestionListeners();
    }

    function showTyping(show) {
      if (typingIndicator) {
        typingIndicator.style.display = show ? 'flex' : 'none';
      }
    }

    function scrollToBottom() {
      setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }, 50);
    }

    function getCurrentTime() {
      const now = new Date();
      return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
    }

    // 7. Lightweight Markdown Formatter
    function parseMarkdown(text) {
      if (!text) return '';
      let html = escapeHtml(text);

      // Headers (### Header)
      html = html.replace(/^### (.*$)/gim, '<h4>$1</h4>');
      html = html.replace(/^## (.*$)/gim, '<h3>$1</h3>');

      // Bold (**text**)
      html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

      // Italics (*text*)
      html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

      // Links ([Label](URL))
      html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');

      // Bullet points (• item or - item)
      const lines = html.split('\n');
      let inList = false;
      let result = [];

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line.startsWith('• ') || line.startsWith('- ')) {
          if (!inList) {
            inList = true;
            result.push('<ul>');
          }
          result.push(`<li>${line.substring(2)}</li>`);
        } else {
          if (inList) {
            inList = false;
            result.push('</ul>');
          }
          if (line.length > 0) {
            result.push(`<p>${line}</p>`);
          }
        }
      }

      if (inList) {
        result.push('</ul>');
      }

      return result.join('');
    }

    function escapeHtml(string) {
      return String(string)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }

    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
  }
})();
