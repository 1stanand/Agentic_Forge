# AGENTS.md

## Codex UI Build Instructions — Forge Agentic Frontend

**You are:** Codex  
**Your job:** Build the Forge frontend — vanilla HTML, CSS, JavaScript  
**Project root:** `D:\Code\Agentic_Forge\`  
**Date:** April 2026

---

## READ EVERYTHING BEFORE WRITING A SINGLE LINE

Read these documents completely before writing any code:

1. `docs/FORGE.md` — What Forge is, what pages exist, what the backend does
2. `docs/FORGE_SRS.md` — Every API endpoint with exact request/response shapes
3. `docs/Design.md` — Complete UI implementation reference, all CSS tokens, all components

Then study these Stitch reference files — both `code.html` and `screen.png` for each:

- `static/stitch_forge_command_center/forge_login/`
- `static/stitch_forge_command_center/forge_ai_chat_assistant/`
- `static/stitch_forge_command_center/forge_atdd_workspace_hero/`
- `static/stitch_forge_command_center/forge_atdd_workspace_light/`
- `static/stitch_forge_command_center/forge_settings/`
- `static/stitch_forge_command_center/forge_technical_interface/DESIGN.md`

The `screen.png` files are visual truth — match them.  
The `code.html` files show component patterns — understand them, do not copy-paste.

Check `CONTEXT.md` in project root — it tells you what the backend has built and what is ready to call.

---

## Who You Are Working With

**Anand** — CAS QA Lead, Nucleus Software. Domain expert.  
**Claude Code** — Built the backend. Its work is reflected in `CONTEXT.md`.  
**CONTEXT.md** — Shared status snapshot. Read it first. Update it when you complete a task.

**CHANGELOG.md** — Append-only handoff log. Read latest entry before starting. Update it after every completed task, before context compaction, and before ending a session.

---

## Operating Mode — Concise, Not Caveman

Use terse technical English by default. Do **not** use broken grammar, meme language, or "caveman mode". Clear UI implementation instructions matter more than saving a tiny number of output tokens.

### Default: Terse Execution Mode

- No greetings or filler.
- Do not restate the whole UI spec.
- Report only: files changed, visual result, verification, blockers.
- Prefer short bullets.
- Do not paste large HTML/CSS/JS blocks unless Anand asks.
- When backend is missing, say exactly which endpoint is missing and show disabled UI state.

### Plan Mode

Use Plan Mode only for risky UI architecture changes, multi-page refactors, or when Anand explicitly asks. Keep plans short: goal, files, steps, risks, verification.

### Context Discipline

- Read `CONTEXT.md` and latest `CHANGELOG.md` entry before starting work.
- Update both files after each task.
- Before compaction/session handoff, add a short changelog entry with files changed, verification, decisions, blockers, and next step.

---

## Hard Rules — Never Break These

- **No CDN. No internet. Forge runs fully offline.**  
  No `cdn.tailwindcss.com`. No `fonts.googleapis.com`. No external URLs anywhere.
- **No React. No npm. No build step.**  
  Plain HTML, CSS, JavaScript. ES6 modules allowed.
- **No alert() or confirm() dialogs.**  
  All user feedback via toast notifications or inline status messages.
- **No hardcoded API paths in individual pages.**  
  All API calls go through `apiFetch()` in `app.js`.
- **No placeholder or mock data in production files.**  
  Every element wired to real API. If backend not ready for a section, show a disabled state, not fake data.
- **No silent failures.**  
  Every API error shows user-facing feedback.
- **Stitch files are reference only.**  
  They live in `static/stitch_forge_command_center/`. Never served to users. Never modified.
- **Do not touch `forge/` directory** — that is Claude Code territory.
- **Do not touch `CLAUDE.md`** — that is Claude Code territory.
- You may update only these root files outside `static/`: `CONTEXT.md` and `CHANGELOG.md`. Do not modify backend or Claude instruction files.

---

## Your File Structure

You build exactly these files. Nothing else.

```
static/
├── index.html              ← Login page
├── chat.html               ← Forge Chat
├── atdd.html               ← ATDD Workspace (most important)
├── settings.html           ← User Settings
├── style.css               ← Design tokens + all shared styles
├── app.js                  ← Shared utilities — auth, API, theme, toast
└── fonts/
    ├── Inter-Variable.ttf
    ├── JetBrainsMono-Regular.ttf
    └── JetBrainsMono-Medium.ttf
```

---

## Step 0 — Fix Offline Dependencies Before Anything Else

The Stitch reference files use CDN resources. Fix these before writing any production file. Verify offline after each fix.

### Tailwind CSS

Do **not** use Tailwind CDN/runtime in production files. Do **not** add `cdn.tailwindcss.com`. Do **not** depend on Tailwind config scripts in browser.

Use `static/style.css` as the production design system. Translate useful Stitch/Tailwind class intent into plain CSS classes and CSS custom properties.

If a precompiled Tailwind CSS file is already provided by Anand, you may link it as a static local asset. Otherwise, do not create or require `tailwind.min.css`.

### Inter Font

- Download `Inter-Variable.ttf` from `https://fonts.google.com/specimen/Inter`
- Save to `static/fonts/Inter-Variable.ttf`

### JetBrains Mono

- Download Regular (400) and Medium (500) TTF from `https://fonts.google.com/specimen/JetBrains+Mono`
- Save to `static/fonts/JetBrainsMono-Regular.ttf` and `static/fonts/JetBrainsMono-Medium.ttf`

### Icons — Material Symbols Replacement

The Stitch files use Material Symbols from Google CDN. Replace every icon with inline SVG from `https://lucide.dev`. Copy SVG source directly into HTML. No external files needed.

### Verify Offline

Disconnect internet. Open each production HTML page in browser after implementation. Fonts, icons, and layout must render correctly. Stitch files are reference only; production pages must not depend on CDN assets.

---

## style.css — Write This First

All design tokens as CSS custom properties. Both themes. All shared component styles.

The complete token set and component patterns are in `docs/Design.md` Sections 3–7. Port them exactly.

Key things that must be in `style.css`:

- All `--variable` definitions for dark theme under `:root, [data-theme="dark"]`
- All `--variable` definitions for light theme under `[data-theme="light"]`
- `@font-face` declarations for Inter and JetBrains Mono
- App shell layout (sidebar + main area grid)
- All button styles: `.btn-primary`, `.btn-secondary`, `.btn-danger`
- All input styles: `.input`, `.input:focus`
- Card styles: `.card`, `.card-glass`
- Badge styles: `.badge`, `.badge-new-step`, `.badge-low-match`, `.badge-role-gap`, `.badge-success`, `.badge-running`
- Context pill: `.context-pill`, `.context-pill-cas`, `.context-pill-general`
- Agent card states: `[data-state="waiting"]`, `[data-state="running"]`, `[data-state="completed"]`, `[data-state="failed"]`
- Animation keyframes: `agent-pulse`, `connector-flow`
- Typography classes: `.text-h1`, `.text-h2`, `.text-body-md`, `.text-body-sm`, `.mono-code`, `.mono-label`, `.mono-metric`
- Toast component styles
- Theme transition: `transition: background 200ms ease, color 200ms ease, border-color 200ms ease` on `:root`

---

## app.js — Write This Second

Shared across all pages. Every page loads this as `<script type="module" src="app.js">`.

Must export or define these functions:

```javascript
// ── AUTH ──────────────────────────────────────────────
function getToken()
// Returns access_token from localStorage or null

function setAuth(token, displayName, userId, isAdmin)
// Stores all auth values in localStorage

function clearAuth()
// Removes access_token, display_name, user_id, is_admin from localStorage

function requireAuth()
// If no token → redirect to index.html immediately
// Call at top of every protected page

function getDisplayName()
// Returns display_name from localStorage

function isAdmin()
// Returns true if is_admin === 'true' in localStorage

// ── API ───────────────────────────────────────────────
async function apiFetch(path, options = {})
// Wrapper around fetch()
// Adds Authorization: Bearer <token> header automatically
// Base URL is same origin — no hardcoded host
// On 401 → clearAuth() + redirect to index.html
// Returns parsed JSON or throws error with message

// ── THEME ─────────────────────────────────────────────
function initTheme()
// Reads forge_theme from localStorage (default: 'dark')
// Sets data-theme on document.body

function toggleTheme()
// Switches dark ↔ light
// Saves to localStorage
// Updates data-theme on document.body

// ── TOAST ─────────────────────────────────────────────
function showToast(message, type = 'info', duration = 3000)
// type: 'success' | 'error' | 'info' | 'warning'
// Appears bottom-right
// Auto-dismisses after duration ms
// Slides in on appear, slides out on dismiss
// Multiple toasts stack vertically

// ── NAVIGATION ────────────────────────────────────────
function logout()
// clearAuth() → redirect to index.html

function setActiveNav(page)
// page: 'chat' | 'atdd' | 'settings'
// Adds active class to correct sidebar nav item

// ── SSE / STREAMING ───────────────────────────────────
function connectProgressStream(jobId, onAgent, onDone, onError)
// Connects to /generate/{jobId}/stream using authenticated fetch() streaming
// Do NOT use native EventSource because it cannot reliably send Authorization headers
// Adds Authorization: Bearer <token> header
// Parses SSE frames formatted as: data: {"agent": N, "elapsed": E}
// onAgent(agentNum, elapsed) — called for each progress event
// onDone() — called when {"status": "done"}
// onError(reason) — called when {"status": "failed", "reason": "..."}
// Returns an AbortController so caller can cancel stream on navigation
// Handles malformed events gracefully — never crashes the UI
```

---

## HTML Page Template

Every protected page shares this shell. Login page is the exception.

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Forge — [Page Name]</title>
    <link rel="stylesheet" href="style.css" />
  </head>
  <body data-theme="dark">
    <div class="app-shell">
      <!-- Sidebar -->
      <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
          <div class="sidebar-logo">
            <!-- Forge wordmark or logo SVG -->
            <span class="text-h2" style="color: var(--primary)">Forge</span>
          </div>
          <button
            onclick="toggleSidebar()"
            class="sidebar-collapse-btn"
            aria-label="Collapse sidebar"
          >
            <!-- chevron icon SVG -->
          </button>
        </div>

        <nav class="sidebar-nav">
          <a href="chat.html" class="nav-item" id="nav-chat">
            <!-- message icon SVG -->
            <span class="nav-label">Forge Chat</span>
          </a>
          <a href="atdd.html" class="nav-item" id="nav-atdd">
            <!-- layers icon SVG -->
            <span class="nav-label">Forge ATDD</span>
          </a>
          <a href="settings.html" class="nav-item" id="nav-settings">
            <!-- settings icon SVG -->
            <span class="nav-label">Settings</span>
          </a>
        </nav>

        <div class="sidebar-footer">
          <div class="user-info">
            <span class="text-body-sm" id="display-name">—</span>
          </div>
          <button onclick="logout()" class="btn-secondary btn-sm">
            <!-- logout icon SVG -->
            <span class="nav-label">Sign Out</span>
          </button>
        </div>
      </aside>

      <!-- Main -->
      <div class="main-area">
        <header class="topbar">
          <div class="topbar-left">
            <span class="text-body-md" style="color: var(--on-surface-variant)"
              >[Page Title]</span
            >
          </div>
          <div class="topbar-right">
            <!-- Theme toggle -->
            <button
              onclick="toggleTheme()"
              id="theme-toggle"
              aria-label="Toggle theme"
            >
              <!-- sun/moon SVG — swap on toggle -->
            </button>
          </div>
        </header>

        <main class="page-content" id="page-content">
          <!-- Page-specific content here -->
        </main>
      </div>
    </div>

    <!-- Toast container -->
    <div
      id="toast-container"
      style="position:fixed; bottom:24px; right:24px; z-index:9999; display:flex; flex-direction:column; gap:8px;"
    ></div>

    <script type="module" src="app.js"></script>
    <script type="module">
      import {
        requireAuth,
        initTheme,
        setActiveNav,
        getDisplayName,
      } from "./app.js";
      requireAuth();
      initTheme();
      setActiveNav("[page]");
      document.getElementById("display-name").textContent =
        getDisplayName() || "User";
    </script>
  </body>
</html>
```

---

## Build Order — One Task at a Time

Complete one task. Show Anand the result. Wait for confirmation. Then next task.

---

### Task 1 — Offline Dependencies + style.css + app.js

- Download/self-host Inter and JetBrains Mono fonts
- Replace Material Symbols usage in production pages with inline Lucide SVG
- Do not use Tailwind CDN/runtime; implement production styling in `static/style.css`
- Write `static/style.css` — all design tokens and shared styles
- Write `static/app.js` — all shared utilities, including authenticated fetch streaming for generation progress

**Verification:**

- Open production HTML pages with internet disconnected — render correctly
- Browser Network tab shows no CDN/external requests
- Browser console shows no 404 errors
- `app.js` imports without errors in browser console

---

### Task 2 — Login Page (index.html)

Reference: `static/stitch_forge_command_center/forge_login/screen.png`

Layout: full-screen centered card. No sidebar. No topbar.

Elements:

- Forge logo/wordmark prominent center-top of card
- "Nucleus Software — Internal Platform" subtitle, muted, small
- Username input (Inter label, JetBrains Mono input)
- Password input (masked)
- Login button — primary, full width
- Error message area — hidden by default, shown on failure, inline below password
- Subtle background pattern — CSS radial gradient + grid lines, no image file
- Theme toggle — top right corner, minimal

Behavior:

```javascript
loginBtn.onclick = async () => {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;
  if (!username || !password) {
    showError("Enter username and password");
    return;
  }

  loginBtn.disabled = true;
  loginBtn.textContent = "Signing in...";

  try {
    const res = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) {
      showError(data.detail || "Invalid credentials");
      return;
    }
    setAuth(data.access_token, data.display_name, data.user_id, data.is_admin);
    window.location.href = "chat.html";
  } catch (e) {
    showError("Connection error. Is Forge running?");
  } finally {
    loginBtn.disabled = false;
    loginBtn.textContent = "Sign In";
  }
};

// If already logged in — skip to chat
if (getToken()) window.location.href = "chat.html";
```

**Verification:**

- Login page loads correctly offline
- Login with correct credentials → redirect to chat.html
- Login with wrong credentials → inline error message, no alert()
- Already logged in → skip directly to chat.html

---

### Task 3 — Chat Page (chat.html)

Reference: `static/stitch_forge_command_center/forge_ai_chat_assistant/screen.png`

Layout: app shell + session history panel + message thread

Three columns within main area:

```
[Sidebar] | [Session History Panel] | [Message Thread + Input]
           collapsible              scrollable + fixed bottom
```

Key elements:

**Session history panel:**

- Load on page init: `GET /chat/sessions`
- Each session: title (first 50 chars of first message) + relative date
- Click session → load: `GET /chat/sessions/{id}` → render messages
- New chat button at top → clear thread, set session_id = null
- Delete session button on hover → `DELETE /chat/sessions/{id}`

**Context pill:**

- Shows above message thread
- Updates after each response
- States: `● CAS Knowledge Active` (amber) | `● ATDD Context Active` (amber muted) | `● General` (muted)

**Message thread:**

- User messages: right-aligned, `surface-container-high` background
- Assistant messages: left-aligned, `surface-container` background
- Code blocks inside assistant messages: JetBrains Mono, `surface-container-lowest` background, line numbers
- Loading state: animated dots while waiting for response
- Auto-scroll to bottom on new message

**Input bar:**

- Textarea — expands up to 4 lines, then scrolls
- Send button — primary, disabled when empty or loading
- Enter to send, Shift+Enter for newline

**Send message behavior:**

```javascript
async function sendMessage(message) {
  appendMessage("user", message);
  showTypingIndicator();

  const res = await apiFetch("/chat/", {
    method: "POST",
    body: JSON.stringify({ message, session_id: currentSessionId }),
  });
  const data = await res.json();

  hideTypingIndicator();
  appendMessage("assistant", data.response);
  updateContextPill(data.context_type);
  const wasNewSession = !currentSessionId;
  currentSessionId = data.session_id;

  // Update session list if new session
  if (wasNewSession) refreshSessionList();
}
```

**Verification:**

- Page loads, session list populates
- Send message → response renders
- Context pill updates per response
- Past session loads correctly
- New chat clears thread
- Theme toggle works

---

### Task 4 — ATDD Workspace (atdd.html)

Reference: `static/stitch_forge_command_center/forge_atdd_workspace_hero/screen.png` (dark)  
Reference: `static/stitch_forge_command_center/forge_atdd_workspace_light/screen.png` (light)

**This is the most important page. Implement it most carefully.**

Three states managed by a state machine — same page, no reload:

```javascript
const STATES = {
  MODULE_SELECT: "module_select",
  FORM: "form",
  PIPELINE: "pipeline",
};

let currentState = STATES.MODULE_SELECT;
let currentJobId = null;

function setState(state) {
  document.querySelectorAll(".atdd-state").forEach((el) => {
    el.style.display = "none";
    el.style.opacity = "0";
  });
  const el = document.getElementById(`state-${state}`);
  el.style.display = "flex";
  setTimeout(() => (el.style.opacity = "1"), 10); // fade in
  currentState = state;
}
```

---

#### State A — Module Selector

Three module cards:

- **CAS** — active, clickable, amber border glow on hover, `badge-success` Active badge
- **LMS** — disabled, greyed out, Coming Soon badge, `cursor: not-allowed`, no click
- **Collections** — disabled, greyed out, Coming Soon badge, no click

```html
<div id="state-module_select" class="atdd-state">
  <div class="module-selector-header">
    <h1 class="text-h1">Select Module</h1>
    <p class="text-body-sm" style="color:var(--on-surface-variant)">
      Choose a module to generate feature files for
    </p>
  </div>
  <div class="module-grid">
    <div class="module-card module-active" onclick="selectModule('cas')">
      <div class="module-badge badge badge-success">Active</div>
      <div class="module-name text-h2">CAS</div>
      <div class="module-desc text-body-sm">Credit Application System</div>
      <div class="module-stats mono-label" id="cas-stats">
        <!-- Loaded from backend: unique steps count -->
      </div>
    </div>
    <div class="module-card module-disabled">
      <div class="module-badge badge">Coming Soon</div>
      <div class="module-name text-h2">LMS</div>
      <div class="module-desc text-body-sm">Loan Management System</div>
    </div>
    <div class="module-card module-disabled">
      <div class="module-badge badge">Coming Soon</div>
      <div class="module-name text-h2">Collections</div>
      <div class="module-desc text-body-sm">Collections Module</div>
    </div>
  </div>
</div>
```

---

#### State B — Generation Form

Back button returns to State A.

Fields in exact order:

1. **Input mode toggle** — two buttons styled as a segmented control: `[JIRA ID]` `[CSV]`
2. **JIRA Story ID input** — shown when JIRA ID selected. Placeholder: `CAS-256008`
3. **CSV textarea** — shown when CSV selected. Placeholder: paste raw CSV content. Monospace font.
4. **Flow Type** — segmented control: `[Ordered]` `[Unordered]`
5. **Three Amigos Notes** — textarea, optional label, placeholder: `Any decisions from 3-amigos meeting...`
6. **Advanced section** — `<details>` element, collapsed by default, label "Advanced Options"
   - JIRA PAT Override — password input, placeholder: `Leave blank to use saved settings`
7. **Generate button** — primary, full width, label "Generate Feature File"

Submit behavior:

```javascript
async function submitGeneration() {
  const mode = getSelectedMode(); // 'jira_id' or 'csv'
  const body = {
    jira_input_mode: mode,
    jira_story_id: mode === "jira_id" ? storyIdInput.value.trim() : null,
    jira_csv_raw: mode === "csv" ? csvInput.value.trim() : null,
    flow_type: getFlowType(), // 'ordered' or 'unordered'
    three_amigos_notes: notesInput.value.trim(),
    module: "cas",
    jira_pat_override: patOverrideInput.value.trim() || null,
  };

  if (mode === "jira_id" && !body.jira_story_id) {
    showToast("Enter a JIRA Story ID", "error");
    return;
  }
  if (mode === "csv" && !body.jira_csv_raw) {
    showToast("Paste CSV content", "error");
    return;
  }

  generateBtn.disabled = true;
  generateBtn.textContent = "Starting...";

  try {
    const res = await apiFetch("/generate/", {
      method: "POST",
      body: JSON.stringify(body),
    });
    const data = await res.json();
    currentJobId = data.job_id;
    setState(STATES.PIPELINE);
    startPipeline(currentJobId);
  } catch (e) {
    showToast(e.message || "Generation failed to start", "error");
    generateBtn.disabled = false;
    generateBtn.textContent = "Generate Feature File";
  }
}
```

---

#### State C — Pipeline + Output

Command-center layout. Two panels side by side.

```
┌─────────────────────────────────────────────────────────────┐
│  HUD STRIP — job status, agent progress, elapsed, confidence │
├──────────────────────────┬──────────────────────────────────┤
│                          │                                  │
│   Agent Pipeline         │   Output Panel                   │
│   (11 agents)            │   [Feature Output] [Gap Report]  │
│                          │   [Agent Logs]                   │
│                          │                                  │
└──────────────────────────┴──────────────────────────────────┘
```

**HUD Strip — always visible during pipeline:**
All values in JetBrains Mono `mono-label` style:

- `STATUS` — `RUNNING` (amber) | `COMPLETE` (green) | `FAILED` (red)
- `AGENT` — `6 / 11`
- `ELAPSED` — `00:01:23` — live counter
- `CONFIDENCE` — `—` until Reporter completes
- `TOKENS/SEC` — `—` (placeholder)

**Agent Pipeline — 11 cards with connectors:**

```javascript
const AGENTS = [
  { num: 1, name: "Reader", activity: "Reading JIRA story" },
  { num: 2, name: "Domain Expert", activity: "Fetching CAS domain context" },
  { num: 3, name: "Scope Definer", activity: "Defining story scope" },
  { num: 4, name: "Coverage Planner", activity: "Planning scenario coverage" },
  { num: 5, name: "Action Decomposer", activity: "Decomposing tester actions" },
  { num: 6, name: "Retriever", activity: "Retrieving repository steps" },
  { num: 7, name: "Composer", activity: "Composing scenarios" },
  { num: 8, name: "ATDD Expert", activity: "Validating ATDD rules" },
  { num: 9, name: "Writer", activity: "Writing feature file" },
  { num: 10, name: "Critic", activity: "Reviewing coverage" },
  { num: 11, name: "Reporter", activity: "Preparing final report" },
];

function buildPipeline() {
  const list = document.getElementById("agent-list");
  list.innerHTML = AGENTS.map(
    (a, i) => `
        <div class="agent-card" id="agent-${a.num}" data-state="waiting" onclick="inspectAgent(${a.num})">
            ${i > 0 ? '<div class="agent-connector" id="connector-' + a.num + '"></div>' : ""}
            <div class="agent-number mono-label">${String(a.num).padStart(2, "0")}</div>
            <div class="agent-status-icon" id="agent-icon-${a.num}">⏸</div>
            <div class="agent-info">
                <div class="agent-name text-body-md">${a.name}</div>
                <div class="agent-activity text-body-sm" id="agent-activity-${a.num}">Waiting...</div>
            </div>
            <div class="agent-elapsed mono-label" id="agent-elapsed-${a.num}">--</div>
        </div>
    `,
  ).join("");
}

function activateAgent(num, elapsed) {
  // Mark previous as complete
  if (num > 1) {
    const prev = document.getElementById(`agent-${num - 1}`);
    if (prev) {
      prev.dataset.state = "completed";
      document.getElementById(`agent-icon-${num - 1}`).textContent = "✓";
      document.getElementById(`agent-connector-${num}`) &&
        document
          .getElementById(`agent-connector-${num}`)
          .classList.remove("active");
    }
  }
  // Activate current
  const card = document.getElementById(`agent-${num}`);
  if (card) {
    card.dataset.state = "running";
    document.getElementById(`agent-icon-${num}`).textContent = "◉";
    document.getElementById(`agent-activity-${num}`).textContent =
      AGENTS[num - 1].activity;
    document.getElementById(`agent-elapsed-${num}`).textContent = `${elapsed}s`;
    const connector = document.getElementById(`connector-${num}`);
    if (connector) connector.classList.add("active");
    card.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
  // Update HUD
  document.getElementById("hud-agent").textContent = `${num} / 11`;
  document.getElementById("hud-elapsed").textContent = formatElapsed(elapsed);
}

function completePipeline() {
  const last = document.getElementById(`agent-11`);
  if (last) {
    last.dataset.state = "completed";
    document.getElementById(`agent-icon-11`).textContent = "✓";
  }
  document.getElementById("hud-status").textContent = "COMPLETE";
  document.getElementById("hud-status").style.color = "var(--success)";
  fetchAndRenderResult();
}

function failPipeline(reason) {
  document.getElementById("hud-status").textContent = "FAILED";
  document.getElementById("hud-status").style.color = "var(--error)";
  showErrorBanner(reason);
  // Find running agent and mark failed
  AGENTS.forEach((a) => {
    const card = document.getElementById(`agent-${a.num}`);
    if (card && card.dataset.state === "running") {
      card.dataset.state = "failed";
      document.getElementById(`agent-icon-${a.num}`).textContent = "✗";
    }
  });
}
```

**SSE connection:**

```javascript
function startPipeline(jobId) {
  buildPipeline();
  resetHUD();
  startElapsedTimer();

  connectProgressStream(
    jobId,
    (agentNum, elapsed) => activateAgent(agentNum, elapsed),
    () => completePipeline(),
    (reason) => failPipeline(reason),
  );
}
```

**Output panel — three tabs:**

Tab 1 — Feature Output:

- Code editor style: black background, line numbers, JetBrains Mono
- Gherkin syntax highlighting — implement `highlightGherkin()` from `docs/Design.md` Section 16
- Copy to clipboard button — top right, shows "Copied!" for 2 seconds
- Download as `.feature` file button
- Marker badges inline on affected lines

Tab 2 — Gap Report:

- Four summary cards: NEW STEPS (amber), LOW MATCH (orange), ROLE GAPS (red), CONFIDENCE (green/amber/red based on score)
- Grouped gap list below cards — each item shows gap description + suggested action
- Empty state when no gaps: "No gaps detected — all steps found in repository"

Tab 3 — Agent Logs:

- Black background `#000`
- JetBrains Mono 12px
- Timestamped entries — format: `[HH:MM:SS] message`
- Color-coded: timestamps muted, INFO normal, MARKER amber, ERROR red
- Auto-scrolls to bottom as entries arrive
- Blinking cursor at bottom while running

**Fetch and render result:**

```javascript
async function fetchAndRenderResult() {
  try {
    const res = await apiFetch(`/generate/${currentJobId}/result`);
    const data = await res.json();

    // Feature file tab
    document.getElementById("feature-output").innerHTML = highlightGherkin(
      data.feature_file,
    );

    // Gap report tab
    renderGapReport(data.gap_report);

    // Confidence in HUD
    if (data.confidence_score) {
      document.getElementById("hud-confidence").textContent =
        Math.round(data.confidence_score * 100) + "%";
    }

    // Switch to feature output tab
    switchTab("feature-output");
  } catch (e) {
    showToast("Failed to load result: " + e.message, "error");
  }
}
```

**Error banner for failed state:**

```html
<div id="error-banner" style="display:none" class="error-banner">
  <span class="error-icon">⚠</span>
  <span id="error-reason">Generation failed</span>
  <button onclick="setState(STATES.FORM)" class="btn-secondary btn-sm">
    Try Again
  </button>
</div>
```

**Verification:**

- Module selector renders — CAS active, others disabled
- CAS click transitions to form without reload
- Form submits → job_id returned → transitions to pipeline
- All 11 agent cards visible, animate in sequence
- HUD updates live
- Feature file renders with syntax highlighting on completion
- Gap report renders
- Failed state shows error and Try Again
- Theme toggle works on all three states

---

### Task 5 — Settings Page (settings.html)

Reference: `static/stitch_forge_command_center/forge_settings/screen.png`

Four sections, each in a `.card`:

**Profile section:**

- Display name input — pre-filled from `GET /settings/`
- Theme selector — radio or toggle: Dark | Light
- Save button → `PUT /settings/profile` with `{display_name}`
- Show inline success/error after save

**JIRA Configuration section:**

- JIRA URL input
- JIRA PAT input — `type="password"` masked
- Both pre-filled from `GET /settings/`
- Save button → `PUT /settings/` with `{jira_url, jira_pat}`
- Test Connection button → `POST /settings/test-jira`
  - Show result inline: green "Connected — Project: CAS" or red "Failed: [reason]"

**Password section:**

- Current password input
- New password input
- Change Password button → `PUT /settings/password`
- Show inline success or error

**System section:**

- Test Model button → `POST /settings/test-model`
  - Show result inline: green "Model loaded — [N] tokens/sec" or red "Model not loaded. Check LLM_MODEL_PATH."
- Offline mode indicator — always shows "● Offline Mode" in amber
- Model name — read from response, display in mono-label style

Load settings on page init:

```javascript
async function loadSettings() {
  const res = await apiFetch("/settings/");
  const data = await res.json();
  document.getElementById("display-name-input").value = data.display_name || "";
  document.getElementById("jira-url").value = data.jira_url || "";
  document.getElementById("jira-pat").value = ""; // never pre-fill PAT
  document.getElementById("jira-pat").placeholder = data.jira_pat
    ? "••••••••"
    : "Not set";
}
```

**Verification:**

- Settings load on page open
- Save profile → success message inline
- Test JIRA → status shown inline, no alert()
- Test Model → status shown inline
- Change password → success or error inline

---

## Error States — Implement These

**LLM not loaded banner** (chat.html and atdd.html):

```html
<div id="llm-warning" class="llm-warning-banner" style="display:none">
  ⚠ LLM model not loaded — Chat and generation are unavailable. Contact admin to
  update LLM_MODEL_PATH and restart the server.
  <button onclick="this.parentElement.style.display='none'">✕</button>
</div>
```

Show this banner when `POST /settings/test-model` returns `status: "error"`. Check on page load.

**Network error:**
Show toast: `Connection error. Check if Forge server is running.`

**Session expired (401):**
`apiFetch()` handles this automatically — clears auth and redirects to login.

---

## Reporting After Each Task

```
Task N — [Name] — COMPLETE

Files modified:
- static/file.html
- static/app.js (if updated)

How to verify:
- [exact steps]

Visual match to Stitch reference:
- [what matches, what differs and why]

Deviations from spec:
- [any decision made differently, with reason]

Ready for Task N+1.
```

Update `CONTEXT.md` after every task. Mark which UI tasks are complete. Then append a concise entry to `CHANGELOG.md` with files changed, verification, decisions, blockers, and next step.

---

## When You Are Stuck

1. Re-read `docs/Design.md` — UI implementation question
2. Look at the Stitch `screen.png` — visual question
3. Look at the Stitch `code.html` — component pattern question
4. Re-read `docs/FORGE_SRS.md` — API contract question
5. Check `CONTEXT.md` — backend status question
6. Check latest `CHANGELOG.md` entry — handoff/current-work question
7. Ask Anand — only for CAS domain clarification

---

_AGENTS.md — Codex UI build instructions._  
_Backend contracts: `docs/FORGE_SRS.md`_  
_UI implementation: `docs/Design.md`_  
_Visual truth: `static/stitch_forge_command_center/` screen.png files_
