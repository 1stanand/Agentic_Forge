---
name: Forge Technical Interface
colors:
  surface: '#161311'
  surface-dim: '#161311'
  surface-bright: '#3c3836'
  surface-container-lowest: '#100e0c'
  surface-container-low: '#1e1b19'
  surface-container: '#221f1d'
  surface-container-high: '#2d2927'
  surface-container-highest: '#383432'
  on-surface: '#e9e1dd'
  on-surface-variant: '#dbc2b0'
  inverse-surface: '#e9e1dd'
  inverse-on-surface: '#33302d'
  outline: '#a38c7c'
  outline-variant: '#554336'
  surface-tint: '#ffb77d'
  primary: '#ffb77d'
  on-primary: '#4d2600'
  primary-container: '#d97707'
  on-primary-container: '#432100'
  inverse-primary: '#904d00'
  secondary: '#ccc5c1'
  on-secondary: '#33302d'
  secondary-container: '#4c4845'
  on-secondary-container: '#beb7b3'
  tertiary: '#ffb694'
  on-tertiary: '#51230a'
  tertiary-container: '#c48060'
  on-tertiary-container: '#491d05'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdcc3'
  primary-fixed-dim: '#ffb77d'
  on-primary-fixed: '#2f1500'
  on-primary-fixed-variant: '#6e3900'
  secondary-fixed: '#e8e1dd'
  secondary-fixed-dim: '#ccc5c1'
  on-secondary-fixed: '#1e1b19'
  on-secondary-fixed-variant: '#4a4643'
  tertiary-fixed: '#ffdbcc'
  tertiary-fixed-dim: '#ffb694'
  on-tertiary-fixed: '#351000'
  on-tertiary-fixed-variant: '#6d391e'
  background: '#161311'
  on-background: '#e9e1dd'
  surface-variant: '#383432'
typography:
  h1:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.02em
  h2:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  mono-code:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  mono-label:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '700'
    lineHeight: 12px
  mono-metric:
    fontFamily: JetBrains Mono
    fontSize: 16px
    fontWeight: '500'
    lineHeight: 20px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  gutter: 1px
  sidebar_width: 240px
  inspector_width: 320px
---

## Brand & Style

This design system is engineered for high-output AI quality assurance professionals who require a dense, data-rich environment that feels like a precision instrument rather than a consumer application. The brand personality is "The Industrial Laboratory"—sophisticated, robust, and technologically advanced. It avoids the clichés of "startup blue" or neon "cyberpunk" aesthetics in favor of a warm, grounded palette that suggests reliability and physical craftsmanship.

The visual style is a hybrid of **Minimalism** and **Glassmorphism**, specifically tailored for "organized complexity." It borrows the functional density of IDEs like VS Code and the structured information hierarchy of Chrome DevTools. The result is a polished, professional atmosphere where every pixel serves a functional purpose, utilizing thin borders and subtle translucency to manage multiple layers of simultaneous data.

## Colors

The palette is anchored in warm neutrals and industrial metallics. The dark theme utilizes "Stone" and "Black" charcoal bases with deep amber undertones to reduce eye strain during long-form technical analysis.

- **Primary Accents:** A spectrum of Amber and Bronze (#D97706 to #B45309) is used for active states, primary actions, and critical data highlights.
- **Surface Palette:** Surfaces use varying levels of Stone (#1C1917) to create a sense of depth without relying on heavy shadows.
- **Functional Colors:** Success, Error, and Warning states are heavily muted to maintain the professional "HUD" feel, ensuring they don't overpower the UI while remaining instantly recognizable.
- **Light Mode:** Reverses the logic using a warm beige "Paper" background (#F5F5F4) with deep bronze typography to maintain the brand’s warmth.

## Typography

This design system employs a dual-font strategy to distinguish between UI navigation and technical data.

1. **Inter:** Used for all standard UI elements, buttons, and instructional text. It provides a clean, neutral foundation that ensures readability at small scales.
2. **JetBrains Mono:** Reserved for the "HUD" (Heads-Up Display) elements, including code blocks, log streams, system metrics, and metadata labels. 

The typography is characterized by high density. Default body sizes are kept at 14px, with 12px and 10px variations used frequently for secondary metadata. Caps and tracking are applied to mono labels to create a sense of "technical headers."

## Layout & Spacing

The layout philosophy follows a **Fixed-Fluid Hybrid** model typical of developer tools. It utilizes a 4px base grid system for micro-spacing.

- **The Workbench:** A 3-pane layout featuring a collapsible navigation sidebar (240px), a fluid central workspace for AI interaction/QA, and a fixed property inspector (320px) on the right.
- **Borders as Spacing:** Unlike consumer apps that use white space to separate elements, this design system uses 1px "technical borders" (#292524) to maximize information density.
- **Density:** Padding is intentionally tight (8px-12px for containers) to allow as much data as possible to be visible above the fold.

## Elevation & Depth

Hierarchy is established through **Tonal Layering** and **Subtle Glassmorphism** rather than traditional drop shadows.

- **Layer 0 (Base):** Deepest charcoal (#0C0A09). Used for the main background.
- **Layer 1 (Panels):** Raised stone (#1C1917). Used for the primary sidebars and header.
- **Layer 2 (Cards/Modals):** A subtle translucent overlay with a `backdrop-filter: blur(12px)`. This creates a "glass" effect that suggests a floating technical layer.
- **Depth Cues:** Depth is reinforced with a "top-light" effect—a 1px inner highlight on the top edge of panels to simulate a physical metallic edge.

## Shapes

The shape language is "Soft-Technical." To maintain the precision of an engineering tool, large rounded corners are avoided. 

- **Primary Radius:** 4px (`0.25rem`) is the standard for buttons, inputs, and cards. This provides just enough softness to feel modern without losing the "industrial" grid feel.
- **Interactive Elements:** Checkboxes and radio buttons maintain sharp/minimalist corners (2px).
- **Icons:** Use linear, 1.5pt stroke weights to match the thin-border aesthetic of the containers.

## Components

- **Buttons:**
  - *Primary:* Solid Bronze background with white Inter SemiBold text. No gradients.
  - *Secondary:* Ghost style with a 1px Stone-700 border and subtle hover state.
- **Inputs:**
  - Dark stone background with a 1px bottom-border focus state in Amber. Use JetBrains Mono for input text to signify "data entry."
- **Chips/Badges:**
  - Small, rectangular with a 2px radius. Use the muted success/error palette with 10% opacity backgrounds and 100% opacity text.
- **Data Tables:**
  - Highly condensed. Row heights are limited to 32px. Use JetBrains Mono for numerical data. Header rows are Stone-800 with mono-label styling.
- **Glass Modals:**
  - Utilize the Layer 2 glassmorphism. Borders should be slightly lighter than the background to define the edge against the blur.
- **Terminal/Log Component:**
  - A dedicated component with a pure black (#000) background, 12px JetBrains Mono text, and color-coded timestamp prefixes.