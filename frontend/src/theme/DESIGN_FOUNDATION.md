# 🌿 AgriNova AI — Design Foundation & System Specification

> **The Stitch project is the single source of truth for AgriNova AI's visual identity.**
> 
> Every screen, component, animation, spacing rule, typography rule, color, interaction, and layout must conform to this design system.
> 
> If implementation and design differ, the Stitch design always takes precedence.

---

## 🏛️ System Identity

AgriNova AI is **NOT** an admin dashboard. It is an **AI Operating System for Precision Agriculture**.

The experience feels like:
- **Mission Control**
- **Environmental Intelligence**
- **Satellite Monitoring**
- **AI Command Center**
- **Premium Apple-level craftsmanship**

Every design decision reinforces this identity.

---

## 🎨 1. Color System

### Earth Canvas & Surfaces
| Token Name | CSS Variable | Hex Value | Purpose |
|---|---|---|---|
| Background Primary | `--color-bg-primary` | `#131412` | Deep Forest Noir (Layer 1 Canvas) |
| Surface Lowest | `--color-bg-subtle` | `#0E0E0D` | Base dark container |
| Surface Low | `--color-bg-surface` | `#1B1C1B` | Field surface container |
| Surface Default | `--color-bg-card` | `#1F201F` | Default card fill |
| Surface High | `--color-bg-surface-high` | `#2A2A29` | Raised surface |
| Surface Highest | `--color-bg-surface-highest` | `#343533` | Command panel fill |
| Soil Deep | `--color-soil-deep` | `#1A1412` | Secondary Fertile Umber topsoil |

### Luminous AI Accents
| Accent Name | CSS Variable | Hex Value | Role |
|---|---|---|---|
| **Neon Mint** | `--color-neon-mint` | `#ADFF00` | Active AI status, Primary buttons, Health score |
| **Crystalline Blue** | `--color-crystalline-blue` | `#E0F2F1` | Spectral UI overlays, Glass lens highlights |
| **Data Stream** | `--color-data-stream` | `#22C55E` | Telemetry feeds, Sensor data points |

### On-Surface Hierarchy
| Token | CSS Variable | Hex | Usage |
|---|---|---|---|
| Primary Text | `--color-text-primary` | `#E4E2E0` | High-contrast headlines & text |
| Secondary Text | `--color-text-secondary` | `#C4C8C1` | Subtitles & secondary labels |
| Muted Text | `--color-text-muted` | `#8D928C` | Captions & technical metadata |
| Text On Mint | `--color-text-on-mint` | `#0E0E0D` | Dark text on solid Neon Mint actions |

---

## ✒️ 2. Typography Hierarchy

| Preset Class | Font Family | Size | Weight | Line Height | Letter Spacing |
|---|---|---|---|---|---|
| `.type-headline-lg` | **Source Serif 4** | 48px (32px mobile) | 600 | 56px | `-0.02em` |
| `.type-headline-md` | **Source Serif 4** | 32px | 600 | 40px | `-0.02em` |
| `.type-headline-sm` | **Source Serif 4** | 24px | 500 | 32px | `0` |
| `.type-body-lg` | **Hanken Grotesk** | 18px | 400 | 28px | `0` |
| `.type-body-md` | **Hanken Grotesk** | 16px | 400 | 24px | `0` |
| `.type-body-sm` | **Hanken Grotesk** | 14px | 400 | 20px | `0` |
| `.type-label-caps` | **JetBrains Mono** | 12px | 500 | 16px | `0.10em` (UPPERCASE) |
| `.type-data-display`| **JetBrains Mono** | 14px | 400 | 20px | `0.02em` |
| `.type-metric` | **JetBrains Mono** | 32px | 700 | 36px | `0.02em` |

---

## 🎬 3. Motion System

Animations communicate system state and must **never** exist purely for decoration.

### Animation Timings
- **Instant**: `100ms` (`--duration-instant`) — Instant state feedback
- **Fast**: `180ms` (`--duration-fast`) — Micro-interactions, button hover/press
- **Normal**: `250ms` (`--duration-normal`) — Card transitions, dropdown disclosures
- **Slow**: `400ms` (`--duration-slow`) — Page transitions, modal slide-ins
- **Ambient**: `4s–8s` (`--duration-ambient`) — Background particles, subtle glow breathing

### Easing Functions
- `ease-out`: `cubic-bezier(0.4, 0, 0.2, 1)` — Standard UI transitions
- `ease-in-out`: `cubic-bezier(0.4, 0, 0.2, 1)` — Ambient breathing & float
- `spring`: `cubic-bezier(0.16, 1, 0.3, 1)` — **Buttons only**

### Interaction Rules
- **Hover**: `transform: translateY(-2px)`
- **Press**: `transform: scale(0.98)`
- **Cards**: `opacity + translateY` transition
- **Pages**: `fade + slide` transition
- **Background**: Always active & slowly running

### Strict Motion Constraints
- ❌ **Never** bounce
- ❌ **Never** rotate UI elements
- ❌ **Never** animate element width
- ❌ **Never** animate layout changes
- ❌ **Never** use flash/strobe effects

---

## 📐 4. Icon System

- **Library**: `lucide-react` **ONLY**
- **Stroke Width**: `1.75` (consistent across all icons)
- **Standard Sizes**: `16px`, `20px`, `24px`, `32px`

### Rules
- Rounded stroke joints (`strokeLinecap="round"`, `strokeLinejoin="round"`)
- Consistent stroke width (`1.75`)
- Same icon library everywhere across all pages and components

### Constraints
- ❌ **No Emojis**
- ❌ **No mixed icon packs**
- ❌ **No filled icons beside outlined icons**

---

## 📐 5. Grid & Layout System

### Layout Blueprint
- **Desktop Sidebar**: `280px` fixed width
- **Content Area**: Max Width `1600px`, centered with `24px` padding
- **Grid Gap**: `24px` base section & card grid gap
- **Tablet**: Collapsed Icon Sidebar (`72px`)
- **Mobile**: Fixed Bottom Navigation Bar (`64px`), `16px` page padding
- **Responsive Grid**: 12-column CSS grid system based on an `8px` spacing unit

---

## 🎛️ 6. Component States

Every component explicitly defines all relevant states:

- **Buttons**: `Default` → `Hover` (`translateY(-2px)`) → `Active` (`scale(0.98)`) → `Loading` → `Disabled` → `Success` → `Error`
- **Cards**: `Default` → `Hover` (`border-color` highlight + `translateY(-2px)`) → `Selected` → `Loading` (Skeleton)
- **Inputs**: `Default` → `Focus` (`#ADFF00` 2px ring) → `Filled` → `Error` (`#FFB4AB` ring) → `Disabled`
- **Sidebar**: `Active` (Neon Mint indicator) → `Hover` → `Selected` → `Collapsed`
- **Navigation**: `Active` → `Hover` → `Disabled`
- **Timeline**: `Upcoming` (muted) → `Current` (Neon Mint active glow) → `Completed` (dark check)
- **Status Badges**: `Success` (`#ADFF00`), `Warning` (`#DEC1B2`), `Error` (`#FFB4AB`), `AI` (`#ADFF00` pulsing dot), `Offline` (`#8D928C`)

---

## 🌌 7. Background System

The ambient living background is active on every single page across 7 layered depth passes:

| Layer | Name | Description | Opacity Rule |
|---|---|---|---|
| **Layer 1** | Forest Canvas | Base background `#131412` | `100%` |
| **Layer 2** | Gradient Shader | Topographic ambient gradient | `100%` |
| **Layer 3** | Ground Glow | Luminous low-frequency earth light | `12%` |
| **Layer 4** | Noise Texture | Organic procedural grain overlay | `2%` |
| **Layer 5** | Fireflies | Floating ambient bio-dots | `15%` |
| **Layer 6** | Seed Particles | Slow upward-drifting spores | `10%` |
| **Layer 7** | Atmospheric Fog | Subtle rolling topsoil mist | `8%` |

---

## 📐 8. Universal Page Formula

Every page in AgriNova AI strictly adheres to this vertical hierarchy:

```
[ 1. Status Label / AI Telemetry Pill ]
                  ↓
[ 2. Large Serif Heading (Source Serif 4) ]
                  ↓
[ 3. Subtitle Description (Hanken Grotesk) ]
                  ↓
[ 4. Primary Glass Command Panel ]
                  ↓
[ 5. Supporting Data Panels Grid ]
                  ↓
[ 6. Primary Action (Neon Mint Button) ]
                  ↓
[ 7. Bottom Navigation (Mobile Only) ]
```

No page should break this structural hierarchy.

---

## 🧩 9. Primitive Component Architecture

Rather than creating dozens of hyper-specialized components (`DashboardButton`, `ScanButton`, `AIButton`, etc.), AgriNova AI is constructed from a tight set of **Primitive Components** with variants:

- `Button` (`variant`: `primary`, `secondary`, `ghost`, `danger`, `telemetry`)
- `Card` (`variant`: `glass`, `soil`, `command`, `telemetry`)
- `Panel` (`variant`: `glass`, `solid`, `command`)
- `Input` (`variant`: `default`, `soil`, `search`)
- `Select`
- `Textarea`
- `Badge` (`status`: `success`, `warning`, `error`, `ai`, `offline`)
- `Chip`
- `Dialog` (Modal lens overlay)
- `Tooltip`
- `Progress` (Circular & Bar fills)
- `Avatar`
- `Navigation` (Sidebar & Bottom Bar)
- `Timeline` (Stage nodes & connected lines)
- `Metric` (Space/JetBrains Mono data callouts)
- `TerminalLabel` (Monospaced telemetry label)
- `StatusDot` (Breathing status dot)

All feature pages are built by composing these primitives.

---

## 🔒 10. Implementation Rules

1. **Design Foundation is LOCKED**: Do NOT redesign components, invent new layouts, create new colors, change typography/spacing, or simplify the UI.
2. **Design System Consumption**: Every new page must consume this Design Foundation. Pages must never define their own ad-hoc visual styles.
3. **One Page at a Time**: Implementation proceeds strictly **one page at a time**.

### Page-by-Page Implementation Order:
1. **Landing**
2. **Login**
3. **Dashboard**
4. **Farms**
5. **Timeline**
6. **Detect**
7. **AI Advisor**
8. **Weather**
9. **Knowledge Base**
10. **Settings**

For every page:
- Read the corresponding Stitch frame.
- Match it as closely as possible.
- Do not reinterpret the design.
- Preserve all backend functionality.
- Replace only the presentation layer.
- Verify the page visually before moving to the next one.
