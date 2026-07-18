const messages = document.getElementById("messages");
const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const resetButton = document.getElementById("resetButton");
const progressBar = document.getElementById("progressBar");
const progressText = document.getElementById("progressText");

function addMessage(text, sender = "bot") {
  const row = document.createElement("div");
  row.className = `message ${sender}`;
  if (sender === "bot") {
    const avatar = document.createElement("div");
    avatar.className = "mini-avatar";
    avatar.textContent = "AI";
    row.appendChild(avatar);
  }
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  row.appendChild(bubble);
  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;
  return row;
}

function showTyping() {
  const row = document.createElement("div");
  row.className = "message bot";
  row.innerHTML = '<div class="mini-avatar">AI</div><div class="bubble"><span class="typing"><i></i><i></i><i></i></span></div>';
  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;
  return row;
}

function setProgress(value) {
  const safe = Math.max(0, Math.min(100, Number(value) || 0));
  progressBar.style.width = `${safe}%`;
  progressText.textContent = `${safe}%`;
}

async function sendMessage(message) {
  const cleaned = message.trim();
  if (!cleaned) return;
  addMessage(cleaned, "user");
  input.value = "";
  input.disabled = true;
  const typing = showTyping();
  try {
    const response = await fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: cleaned }) });
    const data = await response.json();
    typing.remove();
    addMessage(data.reply, "bot");
    setProgress(data.progress);
  } catch (error) {
    typing.remove();
    addMessage("The server could not be reached. Please check that Flask is running.", "bot");
  } finally {
    input.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", event => { event.preventDefault(); sendMessage(input.value); });
document.querySelectorAll("[data-message]").forEach(button => button.addEventListener("click", () => sendMessage(button.dataset.message)));
resetButton.addEventListener("click", async () => {
  await fetch("/api/reset", { method: "POST" });
  messages.innerHTML = "";
  setProgress(0);
  addMessage("Conversation reset. Type 'register' to begin a new registration.");
});

function loadDemo() {
  const demo = new URLSearchParams(window.location.search).get("demo");
  const demos = {
    greeting: [
      ["Hello! I am the AI Registration Assistant. I can help you register or answer internship questions. Type 'register' to begin.", "bot"],
      ["Who can apply?", "user"],
      ["Students and beginners interested in AI, data science, Python, or software development can apply. Basic computer knowledge is enough to start.", "bot"]
    ],
    registration: [
      ["Great! Let us start your registration. Please enter your full name.", "bot"],
      ["Abhinav Singh", "user"], ["Nice to meet you, Abhinav Singh! Please enter your email address.", "bot"],
      ["abhinav@example.com", "user"], ["Email verified. What degree or field are you studying? For example: BTech AI Engineering.", "bot"]
    ],
    completed: [
      ["Please confirm your details:\nName: Abhinav Singh\nEmail: abhinav@example.com\nProgram: BTech AI Engineering\nYear: 2\nExperience: Intermediate\nReply YES to submit or NO to restart.", "bot"],
      ["YES", "user"], ["Registration completed successfully!\nYour registration ID is DAS-20260718-A1B2C3.\nKeep this ID for your records.", "bot"]
    ]
  };
  messages.innerHTML = "";
  if (demo && demos[demo]) {
    demos[demo].forEach(([text, sender]) => addMessage(text, sender));
    setProgress(demo === "completed" ? 100 : demo === "registration" ? 50 : 0);
  } else {
    addMessage("Hello! I am the AI Registration Assistant. I can help you register or answer internship questions. Type 'register' to begin.");
  }
}
loadDemo();
