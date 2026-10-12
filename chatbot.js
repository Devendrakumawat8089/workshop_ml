const API_URL = "/chat";
const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const messages = document.getElementById("messages");
const chatArea = document.getElementById("chatArea");
const welcome = document.getElementById("welcome");
const sendBtn = document.getElementById("sendBtn");
const sidebar = document.getElementById("sidebar");
let sending = false;

function scrollBottom() {
    chatArea.scrollTop = chatArea.scrollHeight;
}

function addMessage(role, text, isError = false) {
    const row = document.createElement("div");
    row.className = `message ${role}`;

    if (role === "assistant") {
        const avatar = document.createElement("div");
        avatar.className = "message-avatar";
        avatar.textContent = "✚";
        row.appendChild(avatar);
    }

    const content = document.createElement("div");
    content.className = "message-content";
    if (isError) content.classList.add("error-message");

    const lines = String(text).split(/\n+/).filter(line => line.trim());
    if (!lines.length) {
        content.textContent = String(text);
    } else {
        lines.forEach(line => {
            const p = document.createElement("p");
            p.textContent = line;
            content.appendChild(p);
        });
    }

    row.appendChild(content);
    messages.appendChild(row);
    scrollBottom();
    return row;
}

function showTyping() {
    const row = document.createElement("div");
    row.className = "message assistant";
    row.id = "typingIndicator";

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = "✚";

    const dots = document.createElement("div");
    dots.className = "typing";
    dots.innerHTML = "<span></span><span></span><span></span>";
    row.append(avatar, dots);
    messages.appendChild(row);
    scrollBottom();
}

async function sendMessage(rawText) {
    const question = rawText.trim();
    if (!question || sending) return;

    welcome.style.display = "none";
    addMessage("user", question);
    input.value = "";
    input.style.height = "auto";
    sending = true;
    sendBtn.disabled = true;
    showTyping();

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: question})
        });

        const data = await response.json();
        document.getElementById("typingIndicator")?.remove();

        if (!response.ok) {
            throw new Error(data.detail || `Request failed (${response.status})`);
        }

        const answer = data.answer ?? data.response ?? data.message;
        if (answer === undefined || answer === null) {
            throw new Error("API response does not contain an answer field.");
        }
        addMessage("assistant", String(answer));
    } catch (error) {
        document.getElementById("typingIndicator")?.remove();
        addMessage("assistant", error.message || "Unable to get a response.", true);
        console.error("Chat request failed:", error);
    } finally {
        sending = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

form.addEventListener("submit", event => {
    event.preventDefault();
    sendMessage(input.value);
});

input.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        form.requestSubmit();
    }
});

input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 160) + "px";
});

document.querySelectorAll(".suggestion").forEach(button => {
    button.addEventListener("click", () => sendMessage(button.dataset.message || ""));
});

document.getElementById("newChatBtn").addEventListener("click", () => {
    messages.replaceChildren();
    welcome.style.display = "";
    input.value = "";
    sidebar.classList.remove("open");
    input.focus();
});

document.getElementById("menuBtn").addEventListener("click", () => {
    sidebar.classList.toggle("open");
});
