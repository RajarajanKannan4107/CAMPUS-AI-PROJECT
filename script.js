// ==========================================================================
// Campus Helper - Client-side Chat Logic
// Vanilla JavaScript (No Frameworks or CDNs)
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {
  const chatMessages = document.getElementById("chatMessages");
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const sendButton = document.getElementById("sendButton");
  const suggestionChips = document.querySelectorAll(".suggestion-chip");

  let isRequestPending = false;

  // Escape HTML entities to prevent XSS
  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // Format bot markdown text (bold and newlines)
  function formatText(text) {
    const escaped = escapeHtml(text);
    return escaped
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n\n/g, "<br><br>")
      .replace(/\n/g, "<br>");
  }

  // Scroll messages to the bottom
  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Append user message bubble
  function appendUserMessage(text) {
    const msgDiv = document.createElement("div");
    msgDiv.className = "message user";

    msgDiv.innerHTML = `
      <div class="message-avatar">👤</div>
      <div class="message-body">
        <div class="message-content">${escapeHtml(text)}</div>
      </div>
    `;

    chatMessages.appendChild(msgDiv);
    scrollToBottom();
  }

  // Append bot message bubble with optional collapsible sources
  function appendBotMessage(answer, sources = []) {
    const msgDiv = document.createElement("div");
    msgDiv.className = "message bot";

    let sourcesHtml = "";
    if (Array.isArray(sources) && sources.length > 0) {
      const sourceItemsHtml = sources
        .map((src, idx) => `
          <div class="source-item">
            <div class="source-item-title">Source Chunk ${idx + 1}</div>
            <div>${escapeHtml(src)}</div>
          </div>
        `)
        .join("");

      sourcesHtml = `
        <details class="sources-details">
          <summary class="sources-summary">
            <span>📚</span>
            <span>View Sources (${sources.length})</span>
          </summary>
          <div class="sources-content">
            ${sourceItemsHtml}
          </div>
        </details>
      `;
    }

    msgDiv.innerHTML = `
      <div class="message-avatar">🎓</div>
      <div class="message-body">
        <div class="message-content">${formatText(answer)}</div>
        ${sourcesHtml}
      </div>
    `;

    chatMessages.appendChild(msgDiv);
    scrollToBottom();
  }

  // Show animated typing indicator
  function showTypingIndicator() {
    const typingDiv = document.createElement("div");
    typingDiv.className = "message bot typing-message";
    typingDiv.id = "typingIndicator";

    typingDiv.innerHTML = `
      <div class="message-avatar">🎓</div>
      <div class="message-body">
        <div class="typing-dots">
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
        </div>
      </div>
    `;

    chatMessages.appendChild(typingDiv);
    scrollToBottom();
  }

  // Remove typing indicator
  function removeTypingIndicator() {
    const indicator = document.getElementById("typingIndicator");
    if (indicator) {
      indicator.remove();
    }
  }

  // Send question to /chat endpoint
  async function submitQuestion(questionText) {
    const question = questionText.trim();
    if (!question || isRequestPending) return;

    isRequestPending = true;
    appendUserMessage(question);
    chatInput.value = "";
    chatInput.disabled = true;
    sendButton.disabled = true;

    showTypingIndicator();

    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      removeTypingIndicator();

      if (!response.ok) {
        const errText = await response.text();
        appendBotMessage(
          `Server returned an error (${response.status}): ${errText || "Please check backend logs."}`,
          []
        );
        return;
      }

      const data = await response.json();
      appendBotMessage(data.answer || "No response received.", data.sources || []);
    } catch (error) {
      removeTypingIndicator();
      appendBotMessage(
        "Unable to connect to the server. Please ensure the backend server is running and try again.",
        []
      );
    } finally {
      isRequestPending = false;
      chatInput.disabled = false;
      sendButton.disabled = false;
      chatInput.focus();
      scrollToBottom();
    }
  }

  // Handle form submission (Send button or Enter key)
  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    submitQuestion(chatInput.value);
  });

  // Handle suggestion chips click
  suggestionChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const question = chip.getAttribute("data-question");
      if (question) {
        submitQuestion(question);
      }
    });
  });
});
