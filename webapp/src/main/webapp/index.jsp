<div style="max-width:720px;margin:2rem auto;font-family:system-ui,Arial,sans-serif;">
  <h1 style="margin:0 0 0.5rem;">Harmony Acupuncture Clinic</h1>
  <p style="margin:0 0 1rem;color:#444;">Ask about booking, hours, services, pricing/insurance, or location.</p>

  <div id="chat" style="border:1px solid #ddd;border-radius:8px;padding:12px;min-height:220px;max-height:360px;overflow:auto;background:#fafafa;"></div>

  <form id="chatForm" onsubmit="return false;" style="display:flex;gap:8px;margin-top:12px;">
    <input id="message" type="text" placeholder="Type your question..." style="flex:1;padding:10px;border:1px solid #ccc;border-radius:6px;" />
    <button id="send" type="button" onclick="sendMessage()" style="padding:10px 16px;border:0;background:#0d6efd;color:white;border-radius:6px;cursor:pointer;">Send</button>
  </form>

  <p style="margin-top:1rem;font-size:0.9rem;color:#666;">Tip: Try asking “How do I book?”, “What are your hours?”, or “How much is a session?”.</p>
</div>

<script>
  const chat = document.getElementById('chat');
  function append(role, text) {
    const row = document.createElement('div');
    row.style.margin = '8px 0';
    const bubble = document.createElement('div');
    bubble.textContent = text;
    bubble.style.display = 'inline-block';
    bubble.style.padding = '8px 10px';
    bubble.style.borderRadius = '8px';
    bubble.style.maxWidth = '85%';
    if (role === 'user') {
      row.style.textAlign = 'right';
      bubble.style.background = '#dbeafe';
    } else {
      row.style.textAlign = 'left';
      bubble.style.background = '#e5e7eb';
    }
    row.appendChild(bubble);
    chat.appendChild(row);
    chat.scrollTop = chat.scrollHeight;
  }

  append('assistant', 'Hi! I’m the Harmony Acupuncture Clinic assistant. Ask me about booking, hours, services, pricing/insurance, or location.');

  async function sendMessage() {
    const input = document.getElementById('message');
    const text = input.value.trim();
    if (!text) return;
    append('user', text);
    input.value = '';
    try {
      const res = await fetch('agent?message=' + encodeURIComponent(text));
      const reply = await res.text();
      append('assistant', reply);
    } catch (e) {
      append('assistant', 'Sorry, something went wrong.');
    }
  }

  document.getElementById('message').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
      sendMessage();
    }
  });
</script>
