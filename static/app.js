const AUTH_KEYS = {
  token: "access_token",
  displayName: "display_name",
  userId: "user_id",
  isAdmin: "is_admin",
  theme: "forge_theme",
};

const TOAST_TYPES = {
  success: "Success",
  error: "Error",
  info: "Info",
  warning: "Warning",
};

function getToken() {
  return localStorage.getItem(AUTH_KEYS.token);
}

function setAuth(token, displayName, userId, isAdminValue) {
  localStorage.setItem(AUTH_KEYS.token, token);
  localStorage.setItem(AUTH_KEYS.displayName, displayName ?? "");
  localStorage.setItem(AUTH_KEYS.userId, String(userId ?? ""));
  localStorage.setItem(AUTH_KEYS.isAdmin, String(Boolean(isAdminValue)));
}

function clearAuth() {
  localStorage.removeItem(AUTH_KEYS.token);
  localStorage.removeItem(AUTH_KEYS.displayName);
  localStorage.removeItem(AUTH_KEYS.userId);
  localStorage.removeItem(AUTH_KEYS.isAdmin);
}

function requireAuth() {
  if (!getToken()) {
    window.location.replace("index.html");
  }
}

function getDisplayName() {
  return localStorage.getItem(AUTH_KEYS.displayName);
}

function setDisplayName(value) {
  localStorage.setItem(AUTH_KEYS.displayName, value ?? "");
  updateDisplayNameElements(value ?? "");
}

function updateDisplayNameElements(value = getDisplayName() || "User") {
  document.querySelectorAll("[data-display-name], #display-name").forEach((element) => {
    element.textContent = value || "User";
  });
}

function isAdmin() {
  return localStorage.getItem(AUTH_KEYS.isAdmin) === "true";
}

async function parseResponsePayload(response) {
  const text = await response.text();
  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = getToken();

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  let response;
  try {
    response = await fetch(path, {
      ...options,
      headers,
    });
  } catch {
    throw new Error("Connection error. Check if Forge server is running.");
  }

  const payload = await parseResponsePayload(response);

  if (response.status === 401) {
    clearAuth();
    window.location.replace("index.html");
    throw new Error("Session expired");
  }

  if (!response.ok) {
    const message =
      (payload && typeof payload === "object" && (payload.detail || payload.message || payload.error)) ||
      (typeof payload === "string" && payload) ||
      `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  response.json = async () => payload;
  return response;
}

function initTheme() {
  const theme = localStorage.getItem(AUTH_KEYS.theme) || "dark";
  document.body.setAttribute("data-theme", theme);
  syncThemeToggle(theme);
  syncThemeChoices(theme);
  return theme;
}

function toggleTheme() {
  const current = document.body.getAttribute("data-theme") || "dark";
  const next = current === "dark" ? "light" : "dark";
  document.body.setAttribute("data-theme", next);
  localStorage.setItem(AUTH_KEYS.theme, next);
  syncThemeToggle(next);
  syncThemeChoices(next);
  return next;
}

function setTheme(theme) {
  const normalized = theme === "light" ? "light" : "dark";
  document.body.setAttribute("data-theme", normalized);
  localStorage.setItem(AUTH_KEYS.theme, normalized);
  syncThemeToggle(normalized);
  syncThemeChoices(normalized);
  return normalized;
}

function syncThemeToggle(theme) {
  const toggle = document.getElementById("theme-toggle");
  if (!toggle) {
    return;
  }

  toggle.setAttribute("aria-label", theme === "dark" ? "Switch to light theme" : "Switch to dark theme");
  toggle.dataset.theme = theme;
  toggle.innerHTML = theme === "dark" ? moonIcon() : sunIcon();
}

function syncThemeChoices(theme) {
  document.querySelectorAll("[data-theme-choice]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.themeChoice === theme);
  });
}

function ensureToastContainer() {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container";
    document.body.appendChild(container);
  }
  return container;
}

function showToast(message, type = "info", duration = 3000) {
  const container = ensureToastContainer();
  const toast = document.createElement("div");
  const safeType = TOAST_TYPES[type] ? type : "info";
  toast.className = `toast toast-${safeType}`;
  toast.innerHTML = `
    <div class="toast-title">${TOAST_TYPES[safeType]}</div>
    <div class="text-body-sm">${escapeHtml(String(message))}</div>
  `;
  container.appendChild(toast);

  requestAnimationFrame(() => {
    toast.classList.add("is-visible");
  });

  const dismiss = () => {
    toast.classList.remove("is-visible");
    toast.classList.add("is-leaving");
    window.setTimeout(() => toast.remove(), 170);
  };

  window.setTimeout(dismiss, duration);
  return dismiss;
}

function logout() {
  clearAuth();
  window.location.replace("index.html");
}

function setActiveNav(page) {
  ["chat", "atdd", "settings"].forEach((name) => {
    const item = document.getElementById(`nav-${name}`);
    if (item) {
      item.classList.toggle("active", name === page);
    }
  });
}

function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  const shell = document.querySelector(".app-shell");
  if (!sidebar) {
    return;
  }

  if (window.matchMedia("(max-width: 960px)").matches) {
    document.body.classList.toggle("sidebar-open");
    return;
  }

  sidebar.classList.toggle("collapsed");
  shell?.classList.toggle("sidebar-collapsed", sidebar.classList.contains("collapsed"));
}

function closeSidebar() {
  document.body.classList.remove("sidebar-open");
}

function parseSseChunk(buffer, onAgent, onDone, onError) {
  const events = buffer.split("\n\n");
  const remainder = events.pop() ?? "";

  for (const rawEvent of events) {
    const dataLines = rawEvent
      .split("\n")
      .filter((line) => line.startsWith("data:"))
      .map((line) => line.slice(5).trim())
      .filter(Boolean);

    if (!dataLines.length) {
      continue;
    }

    try {
      const payload = JSON.parse(dataLines.join("\n"));

      if (typeof payload.agent === "number") {
        onAgent(payload.agent, Number(payload.elapsed ?? 0));
        continue;
      }

      if (payload.status === "done") {
        onDone();
        continue;
      }

      if (payload.status === "failed") {
        onError(payload.reason || "Generation failed");
      }
    } catch {
      // Ignore malformed events.
    }
  }

  return remainder;
}

function connectProgressStream(jobId, onAgent, onDone, onError) {
  const controller = new AbortController();
  const token = getToken();

  if (!token) {
    window.setTimeout(() => onError("Missing authentication token"), 0);
    return controller;
  }

  (async () => {
    let response;

    try {
      response = await fetch(`/generate/${jobId}/stream`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "text/event-stream",
        },
        signal: controller.signal,
      });
    } catch {
      if (!controller.signal.aborted) {
        onError("Connection error. Check if Forge server is running.");
      }
      return;
    }

    if (response.status === 401) {
      clearAuth();
      window.location.replace("index.html");
      onError("Session expired");
      return;
    }

    if (!response.ok || !response.body) {
      onError(`Failed to connect to progress stream (${response.status})`);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    try {
      while (true) {
        const { value, done } = await reader.read();
        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        buffer = parseSseChunk(buffer, onAgent, onDone, onError);
      }

      if (buffer.trim()) {
        parseSseChunk(`${buffer}\n\n`, onAgent, onDone, onError);
      }
    } catch {
      if (!controller.signal.aborted) {
        onError("Progress stream interrupted");
      }
    }
  })();

  return controller;
}

async function checkModelStatus() {
  const response = await apiFetch("/settings/test-model", { method: "POST" });
  const payload = await response.json();
  return {
    success: Boolean(payload?.success),
    message: payload?.message || "",
    raw: payload,
  };
}

function formatRelativeDate(value) {
  if (!value) {
    return "";
  }

  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }

  const seconds = Math.round((Date.now() - date.getTime()) / 1000);
  if (seconds < 60) {
    return "Just now";
  }

  const minutes = Math.round(seconds / 60);
  if (minutes < 60) {
    return `${minutes}m ago`;
  }

  const hours = Math.round(minutes / 60);
  if (hours < 24) {
    return `${hours}h ago`;
  }

  const days = Math.round(hours / 24);
  if (days < 7) {
    return `${days}d ago`;
  }

  return date.toLocaleDateString();
}

function formatClockTime(value) {
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function formatElapsed(totalSeconds) {
  const seconds = Math.max(0, Number(totalSeconds || 0));
  const hours = String(Math.floor(seconds / 3600)).padStart(2, "0");
  const minutes = String(Math.floor((seconds % 3600) / 60)).padStart(2, "0");
  const remainder = String(seconds % 60).padStart(2, "0");
  return `${hours}:${minutes}:${remainder}`;
}

async function copyText(text) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "true");
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.appendChild(textarea);
  textarea.select();

  const ok = document.execCommand("copy");
  textarea.remove();

  if (!ok) {
    throw new Error("Clipboard access unavailable");
  }
}

function downloadTextFile(filename, text) {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function renderInlineText(text) {
  return escapeHtml(String(text || "")).replace(/\n/g, "<br>");
}

function renderMessageContent(text) {
  const safeText = String(text || "");
  const parts = safeText.split(/```/);

  return parts
    .map((part, index) => {
      if (index % 2 === 1) {
        const lines = part.replace(/^\w+\n/, "").split("\n");
        const rows = lines
          .map(
            (line, lineIndex) => `
              <div class="code-row">
                <span class="code-line-no">${lineIndex + 1}</span>
                <span class="code-line-text">${escapeHtml(line)}</span>
              </div>
            `,
          )
          .join("");

        return `
          <div class="code-block">
            <div class="code-block-body">${rows}</div>
          </div>
        `;
      }

      return part
        .split(/\n{2,}/)
        .map((paragraph) => paragraph.trim())
        .filter(Boolean)
        .map((paragraph) => `<p>${renderInlineText(paragraph)}</p>`)
        .join("");
    })
    .join("");
}

function parseLooseObject(value) {
  if (value == null || value === "") {
    return null;
  }

  if (typeof value === "object") {
    return value;
  }

  if (typeof value !== "string") {
    return null;
  }

  try {
    return JSON.parse(value);
  } catch {
    try {
      const normalized = value
        .replace(/\bNone\b/g, "null")
        .replace(/\bTrue\b/g, "true")
        .replace(/\bFalse\b/g, "false")
        .replace(/'/g, '"');
      return JSON.parse(normalized);
    } catch {
      return null;
    }
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function iconPath(strokePath) {
  return `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${strokePath}</svg>`;
}

function moonIcon() {
  return iconPath('<path d="M12 3a6 6 0 1 0 9 9 9 9 0 1 1-9-9Z"></path>');
}

function sunIcon() {
  return iconPath('<circle cx="12" cy="12" r="4"></circle><path d="M12 2v2"></path><path d="M12 20v2"></path><path d="m4.93 4.93 1.41 1.41"></path><path d="m17.66 17.66 1.41 1.41"></path><path d="M2 12h2"></path><path d="M20 12h2"></path><path d="m6.34 17.66-1.41 1.41"></path><path d="m19.07 4.93-1.41 1.41"></path>');
}

Object.assign(window, {
  apiFetch,
  checkModelStatus,
  clearAuth,
  closeSidebar,
  connectProgressStream,
  copyText,
  downloadTextFile,
  escapeHtml,
  formatClockTime,
  formatElapsed,
  formatRelativeDate,
  getDisplayName,
  getToken,
  initTheme,
  isAdmin,
  logout,
  parseLooseObject,
  renderInlineText,
  renderMessageContent,
  requireAuth,
  setActiveNav,
  setAuth,
  setDisplayName,
  setTheme,
  showToast,
  toggleSidebar,
  toggleTheme,
  updateDisplayNameElements,
});

export {
  apiFetch,
  checkModelStatus,
  clearAuth,
  closeSidebar,
  connectProgressStream,
  copyText,
  downloadTextFile,
  escapeHtml,
  formatClockTime,
  formatElapsed,
  formatRelativeDate,
  getDisplayName,
  getToken,
  initTheme,
  isAdmin,
  logout,
  parseLooseObject,
  renderInlineText,
  renderMessageContent,
  requireAuth,
  setActiveNav,
  setAuth,
  setDisplayName,
  setTheme,
  showToast,
  toggleSidebar,
  toggleTheme,
  updateDisplayNameElements,
};
