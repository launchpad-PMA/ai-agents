const state = {
  token: localStorage.getItem("jarvis_token") || "",
  history: [],
};

const $ = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const res = await fetch(path, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw Object.assign(new Error(data.error || "request_failed"), { data, status: res.status });
  return data;
}

function addBubble(role, text) {
  const log = $("log");
  const el = document.createElement("div");
  el.className = `bubble ${role}`;
  el.textContent = text;
  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
}

function speak(text) {
  if (!window.speechSynthesis || !text) return;
  window.speechSynthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.rate = 1;
  window.speechSynthesis.speak(utter);
}

function showApp() {
  $("loginCard").classList.add("hidden");
  $("consoleCard").classList.remove("hidden");
  $("logCard").classList.remove("hidden");
  $("dashCard").classList.remove("hidden");
}

async function refreshDashboard() {
  const dash = await api("/api/dashboard");
  $("modeBadge").textContent = dash.realtime === "mock" ? "mock tools" : "realtime ready";
  $("memoryToggle").checked = dash.memoryEnabled;
  const tools = $("tools");
  tools.innerHTML = "";
  for (const tool of dash.tools) {
    const btn = document.createElement("button");
    btn.className = "tool";
    btn.innerHTML = `<b>${tool.title}</b><span class="risk-${tool.risk}">${tool.risk}</span>`;
    btn.addEventListener("click", () => sendText(`Check ${tool.name}`, tool.risk === "privileged"));
    tools.appendChild(btn);
  }
  if (!state.history.length && dash.history?.length) {
    dash.history.forEach((turn) => addBubble(turn.role, turn.text));
    state.history = dash.history;
  }
}

async function login() {
  $("loginStatus").textContent = "Checking…";
  try {
    const result = await api("/api/login", {
      method: "POST",
      body: JSON.stringify({ code: $("accessCode").value }),
    });
    state.token = result.token;
    localStorage.setItem("jarvis_token", result.token);
    showApp();
    await refreshDashboard();
    await api("/api/realtime/session", { method: "POST", body: "{}" })
      .then((session) => {
        $("micStatus").textContent =
          session.mode === "openai"
            ? "Server minted an OpenAI Realtime session. Key stayed on the backend."
            : session.note || "Mock voice mode.";
      })
      .catch(() => {});
  } catch (error) {
    $("loginStatus").textContent = error.status === 401 ? "Access code rejected." : "Login failed.";
  }
}

async function sendText(text, confirm = false) {
  const value = String(text || "").trim();
  if (!value) return;
  addBubble("user", value);
  $("textInput").value = "";
  try {
    const result = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({ text: value, confirm }),
    });
    addBubble("assistant", result.reply);
    speak(result.spoken || result.reply);
    $("dashStatus").textContent = result.tools?.length ? `${result.tools.length} tool call(s)` : "no tools";
  } catch (error) {
    if (error.status === 401) {
      localStorage.removeItem("jarvis_token");
      location.reload();
      return;
    }
    addBubble("assistant", "Command failed.");
  }
}

function setupPushToTalk() {
  const button = $("ptt");
  const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Speech) {
    $("micStatus").textContent = "This browser has no speech recognition. Type commands, or use Chrome on Galaxy.";
    button.addEventListener("click", () => $("textInput").focus());
    return;
  }
  const recognition = new Speech();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.continuous = false;
  let armed = false;

  const start = () => {
    if (armed) return;
    armed = true;
    button.classList.add("hot");
    button.textContent = "Listening…";
    try {
      recognition.start();
    } catch {
      armed = false;
    }
  };
  const stop = () => {
    button.classList.remove("hot");
    button.textContent = "Hold to talk";
    try {
      recognition.stop();
    } catch {
      /* already stopped */
    }
    armed = false;
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    sendText(transcript);
  };
  recognition.onerror = () => {
    $("micStatus").textContent = "Mic error. Check Chrome microphone permission.";
    stop();
  };
  recognition.onend = stop;

  button.addEventListener("pointerdown", (event) => {
    event.preventDefault();
    start();
  });
  button.addEventListener("pointerup", stop);
  button.addEventListener("pointercancel", stop);
  button.addEventListener("pointerleave", () => {
    if (armed) stop();
  });
}

$("loginBtn").addEventListener("click", login);
$("sendBtn").addEventListener("click", () => sendText($("textInput").value));
$("textInput").addEventListener("keydown", (event) => {
  if (event.key === "Enter") sendText($("textInput").value);
});
$("memoryToggle").addEventListener("change", async (event) => {
  await api("/api/memory", { method: "POST", body: JSON.stringify({ enabled: event.target.checked }) });
});

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js").catch(() => {});
}

api("/api/health")
  .then((health) => {
    $("modeBadge").textContent = health.mode;
    if (state.token) {
      showApp();
      refreshDashboard().catch(() => {
        localStorage.removeItem("jarvis_token");
      });
    }
  })
  .catch(() => {
    $("loginStatus").textContent = "JARVIS backend is not reachable.";
  });

setupPushToTalk();
