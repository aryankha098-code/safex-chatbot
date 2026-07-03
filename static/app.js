const form = document.querySelector("#chat-form");
const input = document.querySelector("#message-input");
const messages = document.querySelector("#messages");
const promptButtons = document.querySelectorAll("[data-question]");
const chatPanel = document.querySelector(".chat-panel");

function createTypingMessage() {
  const article = document.createElement("article");
  article.className = "message bot typing";

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = "SX";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  const paragraph = document.createElement("p");
  paragraph.setAttribute("aria-label", "SafeX assistant is typing");
  for (let index = 0; index < 3; index += 1) {
    const dot = document.createElement("span");
    dot.className = "typing-dot";
    paragraph.appendChild(dot);
  }

  bubble.appendChild(paragraph);
  article.appendChild(avatar);
  article.appendChild(bubble);
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
  return article;
}

function createMessage(role, text, sources = []) {
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "You" : "SX";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  bubble.appendChild(paragraph);

  if (sources.length > 0) {
    const sourceRow = document.createElement("div");
    sourceRow.className = "source-row";
    sources.forEach((source) => {
      const link = document.createElement("a");
      link.href = source.url;
      link.target = "_blank";
      link.rel = "noreferrer";
      link.textContent = source.title;
      sourceRow.appendChild(link);
    });
    bubble.appendChild(sourceRow);
  }

  article.appendChild(avatar);
  article.appendChild(bubble);
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
  return article;
}

async function askQuestion(question) {
  const trimmed = question.trim();
  if (!trimmed) return;

  promptButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.question === trimmed);
  });
  createMessage("user", trimmed);
  input.value = "";
  input.disabled = true;
  form.querySelector("button").disabled = true;

  const pending = createTypingMessage();

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: trimmed }),
    });

    if (!response.ok) {
      throw new Error("Chat request failed");
    }

    const data = await response.json();
    pending.remove();
    createMessage("bot", data.answer, data.sources || []);
  } catch (error) {
    pending.remove();
    createMessage("bot", "Something went wrong while contacting the chatbot API. Please try again.");
  } finally {
    input.disabled = false;
    form.querySelector("button").disabled = false;
    promptButtons.forEach((button) => button.classList.remove("is-active"));
    input.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  askQuestion(input.value);
});

promptButtons.forEach((button) => {
  button.addEventListener("click", () => askQuestion(button.dataset.question || ""));
});

if (chatPanel && window.matchMedia("(pointer: fine)").matches) {
  chatPanel.addEventListener("mousemove", (event) => {
    const rect = chatPanel.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - 0.5;
    const y = (event.clientY - rect.top) / rect.height - 0.5;
    chatPanel.style.setProperty("--tilt-y", `${x * 2.2}deg`);
    chatPanel.style.setProperty("--tilt-x", `${y * -1.8}deg`);
  });

  chatPanel.addEventListener("mouseleave", () => {
    chatPanel.style.setProperty("--tilt-y", "0deg");
    chatPanel.style.setProperty("--tilt-x", "0deg");
  });
}
