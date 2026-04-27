# Design.md

## Forge UI Design System — Implementation Reference

**For:** Codex  
**Source:** Stitch Forge Command Center export  
**Location of Stitch files:** `static/stitch_forge_command_center/`  
**Date:** April 2026

---

## READ THIS FIRST

This document tells you exactly how to implement the Forge UI. The Stitch files in `static/stitch_forge_command_center/` are your visual source of truth. Every page has a `code.html` and a `screen.png`. Study both before writing any code.

Your job is to implement the design into these exact files:

- `static/index.html` — Login
- `static/chat.html` — Forge Chat
- `static/atdd.html` — ATDD Workspace
- `static/settings.html` — Settings
- `static/style.css` — All design tokens and shared styles
- `static/app.js` — Shared auth, API, navigation, theme

**Critical constraint — Forge runs fully offline. No CDN. No cloud assets. Ever.**

The Stitch files use Google Fonts CDN and Tailwind CDN. These will not work offline. Fix them before building. See Section 2.

---

## 1. Stitch File Reference

| Page          | Visual Reference                                                    | Code Reference                                                     |
| ------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Login         | `stitch_forge_command_center/forge_login/screen.png`                | `stitch_forge_command_center/forge_login/code.html`                |
| Chat          | `stitch_forge_command_center/forge_ai_chat_assistant/screen.png`    | `stitch_forge_command_center/forge_ai_chat_assistant/code.html`    |
| ATDD Dark     | `stitch_forge_command_center/forge_atdd_workspace_hero/screen.png`  | `stitch_forge_command_center/forge_atdd_workspace_hero/code.html`  |
| ATDD Light    | `stitch_forge_command_center/forge_atdd_workspace_light/screen.png` | `stitch_forge_command_center/forge_atdd_workspace_light/code.html` |
| Settings      | `stitch_forge_command_center/forge_settings/screen.png`             | `stitch_forge_command_center/forge_settings/code.html`             |
| Design System | `stitch_forge_command_center/forge_technical_interface/DESIGN.md`   | ← Read this                                                        |

---

## 2. Offline Fixes — Do These Before Building Anything

The Stitch files reference external resources that will not work offline. Fix all of these first.

### Fix 1 — Tailwind / CDN Removal

The Stitch exports may contain Tailwind CDN runtime code. Do **not** ship that.

Remove this from every HTML file:

```html
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
```

Allowed implementation options:

**Preferred:** Replace Tailwind utility classes with project-owned CSS in `static/style.css` using the design tokens in this document.

**Acceptable:** Generate a compiled Tailwind CSS file on a dev machine and commit the final local CSS file, for example:

```html
<link rel="stylesheet" href="tailwind.compiled.css" />
```

Hard rules:

- No runtime Tailwind CDN.
- No Google Fonts CDN.
- No external icon/font/image references.
- Do not keep Tailwind config scripts in production HTML unless a local compiled Tailwind workflow explicitly requires them.
- Production pages must work with the network disconnected.

### Fix 2 — Inter Font

Download Inter Variable font:

- URL: `https://fonts.google.com/specimen/Inter`
- Download: `Inter-Variable.ttf` (variable font covers all weights)
- Save to: `static/fonts/Inter-Variable.ttf`

Add to `static/style.css`:

```css
@font-face {
  font-family: "Inter";
  src: url("fonts/Inter-Variable.ttf") format("truetype");
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}
```

### Fix 3 — JetBrains Mono Font

Download JetBrains Mono:

- URL: `https://www.jetbrains.com/lp/mono/` or `https://fonts.google.com/specimen/JetBrains+Mono`
- Download: Regular (400) and Medium (500)
- Save to: `static/fonts/JetBrainsMono-Regular.ttf` and `static/fonts/JetBrainsMono-Medium.ttf`

Add to `static/style.css`:

```css
@font-face {
  font-family: "JetBrains Mono";
  src: url("fonts/JetBrainsMono-Regular.ttf") format("truetype");
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "JetBrains Mono";
  src: url("fonts/JetBrainsMono-Medium.ttf") format("truetype");
  font-weight: 500;
  font-style: normal;
  font-display: swap;
}
```

### Fix 4 — Material Symbols Icons

The Stitch files use Material Symbols from Google CDN. Replace with a local icon approach:

- Download Material Symbols static font file from: `https://github.com/google/material-design-icons/releases`
- Save to: `static/fonts/MaterialSymbols.woff2`
- OR: replace all Material Symbol icon usages with inline SVG icons from `https://lucide.dev` — copy SVG source directly into HTML. No CDN needed.

Lucide is the preferred approach — lighter, no font needed, paste SVG inline.

### Verify Offline

After all fixes — disconnect internet. Open each Stitch HTML file in browser. Fonts, icons, and layout must render correctly. Fix anything that breaks before building production pages.

---

## 3. Design Tokens — CSS Custom Properties

Define all of these in `static/style.css`. Every page links to this file. No hardcoded colors anywhere.

```css
/* ── DARK THEME (default) ─────────────────────────── */
:root,
[data-theme="dark"] {
  /* Surfaces */
  --surface: #161311;
  --surface-dim: #161311;
  --surface-bright: #3c3836;
  --surface-container-lowest: #100e0c;
  --surface-container-low: #1e1b19;
  --surface-container: #221f1d;
  --surface-container-high: #2d2927;
  --surface-container-highest: #383432;

  /* Text */
  --on-surface: #e9e1dd;
  --on-surface-variant: #dbc2b0;
  --inverse-surface: #e9e1dd;
  --inverse-on-surface: #33302d;

  /* Borders */
  --outline: #a38c7c;
  --outline-variant: #554336;
  --border-subtle: #292524;

  /* Primary — Amber/Bronze */
  --primary: #ffb77d;
  --on-primary: #4d2600;
  --primary-container: #d97707;
  --on-primary-container: #432100;
  --primary-fixed: #ffdcc3;
  --primary-fixed-dim: #ffb77d;
  --surface-tint: #ffb77d;

  /* Secondary — Stone */
  --secondary: #ccc5c1;
  --on-secondary: #33302d;
  --secondary-container: #4c4845;
  --on-secondary-container: #beb7b3;

  /* Tertiary — Warm Orange */
  --tertiary: #ffb694;
  --on-tertiary: #51230a;
  --tertiary-container: #c48060;

  /* Functional */
  --error: #ffb4ab;
  --on-error: #690005;
  --error-container: #93000a;
  --success: #4ade80;
  --success-muted: #166534;
  --warning: #fbbf24;
  --warning-muted: #92400e;

  /* Background */
  --background: #161311;
  --on-background: #e9e1dd;

  /* Glass effect */
  --glass-bg: rgba(34, 31, 29, 0.8);
  --glass-border: rgba(163, 140, 124, 0.2);
  --glass-blur: blur(12px);

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.5);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.6);

  /* Top-light effect — metallic edge */
  --top-light: inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

/* ── LIGHT THEME ──────────────────────────────────── */
[data-theme="light"] {
  /* Surfaces — warm paper, not pure white */
  --surface: #f5f5f4;
  --surface-dim: #e7e5e4;
  --surface-bright: #ffffff;
  --surface-container-lowest: #fafaf9;
  --surface-container-low: #f5f5f4;
  --surface-container: #eeedec;
  --surface-container-high: #e9e7e6;
  --surface-container-highest: #e3e1e0;

  /* Text — deep bronze, not pure black */
  --on-surface: #1c1917;
  --on-surface-variant: #57534e;
  --inverse-surface: #1c1917;
  --inverse-on-surface: #f5f5f4;

  /* Borders */
  --outline: #78716c;
  --outline-variant: #d6d3d1;
  --border-subtle: #e7e5e4;

  /* Primary — deeper amber for light bg */
  --primary: #b45309;
  --on-primary: #ffffff;
  --primary-container: #fef3c7;
  --on-primary-container: #78350f;
  --primary-fixed: #fef3c7;
  --primary-fixed-dim: #f59e0b;
  --surface-tint: #b45309;

  /* Secondary */
  --secondary: #57534e;
  --on-secondary: #ffffff;
  --secondary-container: #e7e5e4;
  --on-secondary-container: #1c1917;

  /* Tertiary */
  --tertiary: #9a3412;
  --on-tertiary: #ffffff;
  --tertiary-container: #ffedd5;

  /* Functional */
  --error: #dc2626;
  --on-error: #ffffff;
  --error-container: #fee2e2;
  --success: #16a34a;
  --success-muted: #dcfce7;
  --warning: #d97706;
  --warning-muted: #fef3c7;

  /* Background */
  --background: #f5f5f4;
  --on-background: #1c1917;

  /* Glass effect */
  --glass-bg: rgba(245, 245, 244, 0.85);
  --glass-border: rgba(120, 113, 108, 0.2);
  --glass-blur: blur(12px);

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.08);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.15);

  /* Top-light */
  --top-light: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}
```

---

## 4. Typography Scale

```css
/* ── TYPOGRAPHY ───────────────────────────────────── */
body {
  font-family: "Inter", system-ui, sans-serif;
  font-size: 14px;
  line-height: 20px;
  color: var(--on-surface);
  background: var(--background);
}

.text-h1 {
  font-family: "Inter";
  font-size: 24px;
  font-weight: 600;
  line-height: 32px;
  letter-spacing: -0.02em;
}
.text-h2 {
  font-family: "Inter";
  font-size: 18px;
  font-weight: 600;
  line-height: 24px;
  letter-spacing: -0.01em;
}
.text-body-md {
  font-family: "Inter";
  font-size: 14px;
  font-weight: 400;
  line-height: 20px;
}
.text-body-sm {
  font-family: "Inter";
  font-size: 12px;
  font-weight: 400;
  line-height: 16px;
}

.mono-code {
  font-family: "JetBrains Mono";
  font-size: 13px;
  font-weight: 400;
  line-height: 18px;
}
.mono-label {
  font-family: "JetBrains Mono";
  font-size: 10px;
  font-weight: 700;
  line-height: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.mono-metric {
  font-family: "JetBrains Mono";
  font-size: 16px;
  font-weight: 500;
  line-height: 20px;
}
```

**Rule:** Inter for all UI. JetBrains Mono for code blocks, logs, metrics, HUD values, feature file output, input fields where data is entered.

---

## 5. Spacing System

Base unit: 4px. All spacing is a multiple of 4.

```css
/* Spacing */
--space-xs: 4px;
--space-sm: 8px;
--space-md: 16px;
--space-lg: 24px;
--space-xl: 32px;

/* Layout dimensions */
--sidebar-width: 240px;
--sidebar-collapsed: 56px;
--inspector-width: 320px;
--topbar-height: 48px;
```

Padding inside containers: 8px–12px. Dense. Information-rich. Not airy.

---

## 6. Border Radius

```css
--radius-sm: 2px; /* checkboxes, radio, badges */
--radius-md: 4px; /* buttons, inputs, cards — PRIMARY */
--radius-lg: 8px; /* modals, drawers */
--radius-full: 9999px; /* pills, context indicators */
```

**Rule:** 4px is the default for everything. Never use large rounded corners on cards or panels. This is a precision instrument, not a consumer app.

---

## 7. Component Patterns

### Buttons

```css
/* Primary */
.btn-primary {
  background: var(--primary-container); /* amber/bronze #d97707 */
  color: var(--on-primary);
  font-family: "Inter";
  font-size: 14px;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  border: none;
  cursor: pointer;
  transition: opacity 150ms ease;
}
.btn-primary:hover {
  opacity: 0.9;
}
.btn-primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Secondary / Ghost */
.btn-secondary {
  background: transparent;
  color: var(--on-surface);
  border: 1px solid var(--outline-variant);
  font-family: "Inter";
  font-size: 14px;
  font-weight: 400;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background 150ms ease;
}
.btn-secondary:hover {
  background: var(--surface-container-high);
}

/* Danger */
.btn-danger {
  background: var(--error-container);
  color: var(--error);
  border: none;
}
```

### Inputs

```css
.input {
  background: var(--surface-container-low);
  border: 1px solid var(--outline-variant);
  border-bottom: 1px solid var(--outline);
  color: var(--on-surface);
  font-family: "JetBrains Mono"; /* data entry = mono */
  font-size: 13px;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  width: 100%;
  transition: border-color 150ms ease;
}
.input:focus {
  outline: none;
  border-bottom-color: var(--primary);
}
.input::placeholder {
  color: var(--outline);
}
```

### Cards

```css
.card {
  background: var(--surface-container);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  box-shadow: var(--top-light), var(--shadow-sm);
  padding: 12px;
}

.card-glass {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}
```

### Badges / Markers

```css
.badge {
  font-family: "JetBrains Mono";
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
}
.badge-new-step {
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.3);
}
.badge-low-match {
  background: rgba(251, 146, 60, 0.15);
  color: #fb923c;
  border: 1px solid rgba(251, 146, 60, 0.3);
}
.badge-role-gap {
  background: rgba(248, 113, 113, 0.15);
  color: #f87171;
  border: 1px solid rgba(248, 113, 113, 0.3);
}
.badge-success {
  background: rgba(74, 222, 128, 0.15);
  color: #4ade80;
  border: 1px solid rgba(74, 222, 128, 0.3);
}
.badge-running {
  background: rgba(255, 183, 125, 0.15);
  color: #ffb77d;
  border: 1px solid rgba(255, 183, 125, 0.3);
}
```

### Context Pill (Chat)

```css
.context-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-family: "JetBrains Mono";
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.context-pill-cas {
  background: rgba(255, 183, 125, 0.15);
  color: var(--primary);
  border: 1px solid rgba(255, 183, 125, 0.3);
}
.context-pill-general {
  background: var(--surface-container);
  color: var(--on-surface-variant);
  border: 1px solid var(--border-subtle);
}

/* Dot indicator */
.context-pill::before {
  content: "";
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}
```

---

## 8. Global Layout

### Shell Structure — Every Protected Page

```html
<body data-theme="dark">
  <div class="app-shell">
    <!-- Sidebar -->
    <aside class="sidebar" id="sidebar">
      <div class="sidebar-logo"><!-- Forge logo --></div>
      <nav class="sidebar-nav">
        <a href="chat.html" class="nav-item"><!-- Chat icon + label --></a>
        <a href="atdd.html" class="nav-item"><!-- ATDD icon + label --></a>
        <a href="settings.html" class="nav-item"
          ><!-- Settings icon + label --></a
        >
      </nav>
      <div class="sidebar-footer"><!-- User display name + logout --></div>
    </aside>

    <!-- Main area -->
    <div class="main-area">
      <header class="topbar">
        <!-- Page title left, theme toggle + user right -->
      </header>
      <main class="page-content">
        <!-- Page-specific content -->
      </main>
    </div>
  </div>
</body>
```

```css
.app-shell {
  display: grid;
  grid-template-columns: var(--sidebar-width) 1fr;
  height: 100vh;
  overflow: hidden;
  background: var(--background);
}

.sidebar {
  background: var(--surface-container-low);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  height: 100vh;
  box-shadow: var(--top-light);
}

.main-area {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.topbar {
  height: var(--topbar-height);
  background: var(--surface-container-low);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-md);
  flex-shrink: 0;
}

.page-content {
  flex: 1;
  overflow-y: auto;
}

/* Sidebar collapse */
.sidebar.collapsed {
  width: var(--sidebar-collapsed);
}
.sidebar.collapsed .nav-label {
  display: none;
}
.sidebar.collapsed .sidebar-logo-text {
  display: none;
}
```

---

## 9. Page: Login (index.html)

Reference: `stitch_forge_command_center/forge_login/`

Layout: centered card on full-screen background with subtle pattern.

```html
<body data-theme="dark" class="login-page">
  <div class="login-bg"><!-- subtle abstract system pattern --></div>
  <div class="login-card card-glass">
    <div class="login-logo"><!-- Forge logo --></div>
    <p class="login-subtitle text-body-sm">
      Nucleus Software — Internal Platform
    </p>
    <form id="login-form">
      <div class="form-group">
        <label class="text-body-sm">Username</label>
        <input
          type="text"
          id="username"
          class="input"
          autocomplete="username"
        />
      </div>
      <div class="form-group">
        <label class="text-body-sm">Password</label>
        <input
          type="password"
          id="password"
          class="input"
          autocomplete="current-password"
        />
      </div>
      <div
        id="login-error"
        class="error-msg text-body-sm"
        style="display:none"
      ></div>
      <button
        type="button"
        id="login-btn"
        class="btn-primary"
        style="width:100%"
      >
        Sign In
      </button>
    </form>
    <p class="login-footer text-body-sm">
      Access restricted to Nucleus Software QA team
    </p>
  </div>
</body>
```

Background pattern: use CSS `radial-gradient` and subtle grid lines — no image file needed.

---

## 10. Page: Chat (chat.html)

Reference: `stitch_forge_command_center/forge_ai_chat_assistant/`

Three-column feel: sidebar (shared) + session history panel + message thread.

Key elements:

- **Session history panel** — collapsible, left of message thread, lists past sessions with title + date
- **Context pill** — top of message area, shows `● CAS Knowledge Active` or `● General`
- **Message thread** — scrollable, user messages right-aligned, assistant left-aligned
- **Input bar** — fixed bottom, textarea that expands, send button

Message bubble styling:

```css
.message-user {
  align-self: flex-end;
  background: var(--surface-container-high);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg) var(--radius-sm) var(--radius-lg)
    var(--radius-lg);
  padding: 10px 14px;
  max-width: 70%;
}
.message-assistant {
  align-self: flex-start;
  background: var(--surface-container);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm) var(--radius-lg) var(--radius-lg)
    var(--radius-lg);
  padding: 10px 14px;
  max-width: 80%;
}
/* Code blocks inside assistant messages */
.message-assistant pre {
  font-family: "JetBrains Mono";
  font-size: 12px;
  background: var(--surface-container-lowest);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 10px;
  overflow-x: auto;
  margin-top: 8px;
}
```

---

## 11. Page: ATDD Workspace (atdd.html)

Reference: `stitch_forge_command_center/forge_atdd_workspace_hero/` (dark)  
Reference: `stitch_forge_command_center/forge_atdd_workspace_light/` (light)

**This is the most important screen. Implement it most carefully.**

### Three States — Same Page, No Reload

Use a state machine in JavaScript:

```javascript
const STATES = {
  MODULE_SELECT: "module_select",
  FORM: "form",
  PIPELINE: "pipeline",
};
let currentState = STATES.MODULE_SELECT;

function setState(state) {
  document
    .querySelectorAll(".atdd-state")
    .forEach((el) => (el.style.display = "none"));
  document.getElementById(`state-${state}`).style.display = "flex";
  currentState = state;
}
```

### State A — Module Selector

```html
<div id="state-module_select" class="atdd-state">
  <div class="module-grid">
    <div class="module-card active" onclick="setState('form')">
      <div class="module-icon"><!-- CAS icon --></div>
      <div class="module-name text-h2">CAS</div>
      <div class="module-desc text-body-sm">Credit Application System</div>
      <div class="badge badge-success">Active</div>
    </div>
    <div class="module-card disabled">
      <div class="module-name text-h2">LMS</div>
      <div class="badge">Coming Soon</div>
    </div>
    <div class="module-card disabled">
      <div class="module-name text-h2">Collections</div>
      <div class="badge">Coming Soon</div>
    </div>
  </div>
</div>
```

### State B — Generation Form

Fields in order:

1. Input mode toggle: `[JIRA ID] [CSV]` — radio button style
2. JIRA Story ID input (shown when JIRA ID selected)
3. CSV textarea (shown when CSV selected)
4. Flow Type: `[Ordered] [Unordered]` — radio button style
5. Three Amigos Notes textarea (optional)
6. `<details>` Advanced section — collapsed by default:
   - JIRA PAT Override (password input)
7. Generate button — full width, primary

Back button top-left returns to State A.

### State C — Pipeline + Output

Command-center layout:

```
┌─────────────────────────┬─────────────────────────┐
│   HUD (top strip)       │   HUD (top strip)        │
├─────────────────────────┼─────────────────────────┤
│                         │                          │
│   11-Agent Pipeline     │   Output Panel           │
│   (left/center)         │   (right)                │
│                         │                          │
└─────────────────────────┴─────────────────────────┘
```

CSS:

```css
.pipeline-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto 1fr;
  gap: 1px;
  height: 100%;
  background: var(--border-subtle);
}
.hud-strip {
  grid-column: 1 / -1;
  background: var(--surface-container-lowest);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  padding: 8px var(--space-md);
  font-family: "JetBrains Mono";
  font-size: 10px;
}
```

### HUD Strip Elements

All values in JetBrains Mono:

- `STATUS: RUNNING` (amber when running, green when done, red when failed)
- `AGENT: 6 / 11`
- `ELAPSED: 00:01:23`
- `CONFIDENCE: —` (shows score when available)
- `TOKENS/SEC: —` (placeholder only)
- `LATENCY: —` (placeholder only)

### Agent Pipeline Visualization

11 agent cards in a vertical list with connectors between them.

```html
<div class="pipeline-panel">
  <div class="agent-list">
    <!-- Repeat for each agent -->
    <div class="agent-card" id="agent-1" data-state="waiting">
      <div class="agent-connector top"></div>
      <div class="agent-number mono-label">01</div>
      <div class="agent-status-icon"><!-- icon changes per state --></div>
      <div class="agent-info">
        <div class="agent-name text-body-md">Reader</div>
        <div class="agent-activity text-body-sm">Waiting...</div>
      </div>
      <div class="agent-elapsed mono-label">--</div>
      <div class="agent-connector bottom"></div>
    </div>
  </div>
</div>
```

Agent card states:

```css
.agent-card {
  background: var(--surface-container);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 200ms ease;
  cursor: pointer;
}
.agent-card[data-state="waiting"] {
  opacity: 0.5;
}
.agent-card[data-state="running"] {
  border-color: var(--primary);
  background: var(--surface-container-high);
  box-shadow:
    0 0 0 1px var(--primary),
    var(--shadow-md);
  animation: agent-pulse 1.5s ease-in-out infinite;
}
.agent-card[data-state="completed"] {
  border-color: var(--success-muted);
  opacity: 0.85;
}
.agent-card[data-state="failed"] {
  border-color: var(--error-container);
  background: rgba(147, 0, 10, 0.1);
}

@keyframes agent-pulse {
  0%,
  100% {
    box-shadow:
      0 0 0 1px var(--primary),
      0 0 8px rgba(255, 183, 125, 0.3);
  }
  50% {
    box-shadow:
      0 0 0 1px var(--primary),
      0 0 16px rgba(255, 183, 125, 0.5);
  }
}
```

### Connector between agents

```css
.agent-connector {
  position: absolute;
  left: 50%;
  width: 2px;
  height: 12px;
  background: var(--border-subtle);
  transform: translateX(-50%);
}
.agent-connector.active {
  background: var(--primary);
  animation: connector-flow 0.8s linear infinite;
}
@keyframes connector-flow {
  0% {
    opacity: 0.3;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.3;
  }
}
```

### Output Panel — Three Tabs

```
[Feature Output] [Gap Report] [Agent Logs]
```

**Feature Output tab:**

- Code editor style
- Line numbers (absolute positioned)
- JetBrains Mono 13px
- Gherkin syntax highlighting via CSS classes:
  - `.kw-feature` — `#93c5fd` (blue)
  - `.kw-scenario` — `#c4b5fd` (purple)
  - `.kw-tag` — `#f9a8d4` (pink)
  - `.kw-given` — `#93c5fd` (blue)
  - `.kw-when` — `#fde68a` (yellow)
  - `.kw-then` — `#86efac` (green)
  - `.kw-and` — `#67e8f9` (cyan)
  - `.kw-comment` — `rgba(148,163,184,0.7)` (muted)
- Copy button top right
- Download as .feature button top right
- Marker badges inline after affected steps

**Gap Report tab:**

- Summary cards: NEW STEPS count, LOW MATCH count, ROLE GAPS count, CONFIDENCE score
- Grouped list of gaps with severity
- Each gap shows suggested action

**Agent Logs tab:**

- Black background: `#000`
- JetBrains Mono 12px
- Color-coded by log level:
  - Timestamps: `rgba(148,163,184,0.6)` (muted)
  - INFO: `var(--on-surface-variant)`
  - Markers: `var(--warning)`
  - Errors: `var(--error)`
- Live cursor pulse at bottom when running

---

## 12. Page: Settings (settings.html)

Reference: `stitch_forge_command_center/forge_settings/`

Four sections — use card per section:

1. **Profile** — Display name input, theme toggle (dark/light)
2. **JIRA Configuration** — JIRA URL input, PAT input (masked), Test Connection button
3. **Password** — Current password, new password, Change Password button
4. **System** — Test Model button, model status card showing loaded/not loaded

Test buttons show inline status — do not use alerts.

---

## 13. Theme Toggle

```javascript
// In app.js
function initTheme() {
  const saved = localStorage.getItem("forge_theme") || "dark";
  document.body.setAttribute("data-theme", saved);
}

function toggleTheme() {
  const current = document.body.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  document.body.setAttribute("data-theme", next);
  localStorage.setItem("forge_theme", next);
}
```

Toggle button: sun icon (light mode) / moon icon (dark mode). Top right of topbar. Present on every page.

Transition: `transition: background 200ms ease, color 200ms ease, border-color 200ms ease` on `:root`.

---

## 14. Animation Guidelines

| Interaction              | Duration | Easing               |
| ------------------------ | -------- | -------------------- |
| Button hover             | 150ms    | ease                 |
| Input focus              | 150ms    | ease                 |
| Tab switch               | 150ms    | ease                 |
| Sidebar collapse         | 250ms    | ease-in-out          |
| State transitions (ATDD) | 200ms    | ease                 |
| Agent activation         | 200ms    | ease                 |
| Agent pulse              | 1500ms   | ease-in-out infinite |
| Connector flow           | 800ms    | linear infinite      |
| Toast appear             | 200ms    | ease-out             |
| Toast dismiss            | 150ms    | ease-in              |
| Theme toggle             | 200ms    | ease                 |

No animation should feel decorative. Every animation communicates state change.

---

## 15. app.js — Shared Utilities

All pages import `app.js`. It provides:

```javascript
// Auth
function getToken()               // reads localStorage
function setToken(token)          // writes localStorage
function clearAuth()              // removes token, display_name, user_id
function requireAuth()            // redirects to index.html if no token
function getDisplayName()         // reads localStorage
function isAdmin()                // reads localStorage

// API
async function apiFetch(path, options = {})  // adds Authorization header automatically
// Usage: await apiFetch('/chat/', { method: 'POST', body: JSON.stringify({...}) })

// Theme
function initTheme()              // applies saved theme on page load
function toggleTheme()            // switches and saves theme

// Navigation
function logout()                 // clearAuth() + redirect to index.html

// Toast notifications
function showToast(message, type) // type: 'success' | 'error' | 'info'
// Toast appears bottom-right, auto-dismisses after 3s

// ATDD SSE / streaming progress
async function connectProgressStream(jobId, onAgent, onDone, onError)
// Uses fetch() streaming, not EventSource, because protected routes require Authorization headers.
// GET /generate/{jobId}/stream with Authorization: Bearer <token>
// Parses lines beginning with: data: {...}
// onAgent(agentNum, elapsed) — called per progress event
// onDone() — called when done
// onError(reason) — called when failed
```

Implementation rule: do not use native `EventSource` for this protected stream unless backend auth is changed to HttpOnly cookie auth. `EventSource` cannot reliably send custom Authorization headers.

---

## 16. Gherkin Syntax Highlighter

Implement as a JavaScript function in `atdd.html`:

```javascript
function highlightGherkin(text) {
  const lines = text.split("\n");
  return lines
    .map((line, i) => {
      const num = `<span class="line-no">${String(i + 1).padStart(3, " ")}</span>`;
      let cls = "";
      const trimmed = line.trimStart();
      if (trimmed.startsWith("Feature:")) cls = "kw-feature";
      else if (trimmed.startsWith("Scenario Outline:")) cls = "kw-scenario";
      else if (trimmed.startsWith("Scenario:")) cls = "kw-scenario";
      else if (trimmed.startsWith("Background:")) cls = "kw-scenario";
      else if (trimmed.startsWith("@")) cls = "kw-tag";
      else if (trimmed.startsWith("Given ")) cls = "kw-given";
      else if (trimmed.startsWith("When ")) cls = "kw-when";
      else if (trimmed.startsWith("Then ")) cls = "kw-then";
      else if (trimmed.startsWith("And ")) cls = "kw-and";
      else if (trimmed.startsWith("#")) cls = "kw-comment";
      else if (trimmed.startsWith("|")) cls = "kw-table";
      else if (trimmed.startsWith("Examples:")) cls = "kw-scenario";
      const code = `<span class="line-code ${cls}">${escapeHtml(line)}</span>`;
      return `<div class="editor-line">${num}${code}</div>`;
    })
    .join("");
}

function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
```

---

## 17. Error States

**LLM not loaded:**
Show a dismissible banner at top of Chat and ATDD pages:

```
⚠ LLM model not loaded. Chat and generation are unavailable.
  Contact admin to update LLM_MODEL_PATH and restart the server.
```

Style: amber background, `var(--warning-muted)`, full width, dismissible.

**Generation failed:**
Show error banner in pipeline view with the failure reason from the SSE stream. Highlight the failed agent card. Show retry affordance if applicable.

**Network error:**
Show toast: `Connection error. Check if Forge server is running.`

---

## 18. Definition of Done

Codex must not consider the UI complete until every item passes:

- All fonts load offline — Inter and JetBrains Mono
- No CDN references in any file
- A disconnected-network browser test passes for login, chat shell, ATDD shell, and settings shell
- Theme toggle works on all pages and persists on refresh
- Login flow: submit → token stored → redirect to chat
- Invalid token on protected page → redirect to login
- Logout → token cleared → redirect to login
- Chat: send message → response renders → session saved
- ATDD: module select → form → generate → progress → output all work
- Progress stream works using authenticated `fetch()` streaming, not unauthenticated `EventSource`
- All 11 agent cards animate correctly during generation
- HUD updates live during generation
- Feature file renders with syntax highlighting
- Gap report renders with marker counts
- Agent logs tab shows timestamped entries
- Settings: load, save, test-jira, test-model all work
- Error states display correctly (LLM not loaded, generation failed)
- Stitch design fidelity: colors, spacing, typography match screen.png references

---

_Design.md — UI implementation reference for Codex._  
_Visual truth: `static/stitch_forge_command_center/` screen.png files._  
_Backend contracts: `docs/FORGE_SRS.md`._
