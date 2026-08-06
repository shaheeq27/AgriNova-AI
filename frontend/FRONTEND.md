# 🌱 AgriNova AI — Frontend Design System & Architecture (v1.1)

## Overview
AgriNova AI's frontend is a modular, high-performance web application designed with a futuristic dark forest aesthetic ("Apple-level agricultural OS"). It uses Next.js 15, TypeScript, Vanilla CSS design tokens, and CSS Modules.

---

## 📂 Folder Structure

```text
src/
├── app/                  # Next.js App Router (Pages & Layouts)
├── background/           # Living Background Engine (Shader, GroundGlow, Fog, Fireflies, SeedParticles, Noise)
├── components/           # Component Library
│   ├── buttons/          # PrimaryButton, SecondaryButton, GhostButton, IconButton
│   ├── cards/            # Card, GlassCard, MetricCard, StatusCard, WeatherCard, etc.
│   ├── forms/            # Input, Search, Select, TextArea, Toggle
│   ├── typography/       # Title, Heading, Subtitle, Label, Metric, Caption
│   ├── status/           # Badge, PulseDot, StatusIndicator, OnlineStatus
│   ├── common/           # Modal, Tooltip, Avatar, Divider
│   ├── layout/           # Navbar, Sidebar, BottomNavigation, MobileHeader, PageContainer, Section
│   └── ui/               # Core UI Barrel Exports
├── config/               # App configuration (API endpoints, metadata)
├── constants/            # Shared constants (Nav links, soil types, crop stages)
├── effects/              # Animation System (Fade, Slide, PageTransition, LogoFloat, AuraPulse, HoverLift, etc.)
├── features/             # Feature Modules & Templates (DashboardTemplate, DetectTemplate, AdvisorTemplate, etc.)
├── hooks/                # Custom React Hooks (useAnimation, useCounter, useParticles, useScroll, useTheme)
├── layouts/              # Shared Layout HOCs & Templates
├── providers/            # React Context Providers (AuthProvider)
├── styles/               # CSS Design Tokens (colors, typography, spacing, radius, shadows, animations)
├── theme/                # TypeScript Token Constants & Breakpoints
├── ui/                   # Re-export alias for @/components/ui
└── utils/                # Helper utilities (cn class merger)
```

---

## 🎨 Color Palette & CSS Variables

| Category | CSS Variable | Hex / RGBA Value | Usage |
| :--- | :--- | :--- | :--- |
| **Backgrounds** | `--color-bg-primary` | `#040a06` | Main app background |
| | `--color-bg-surface` | `#0b170e` | Card & container surfaces |
| | `--color-bg-glass` | `rgba(11, 23, 14, 0.7)` | Backdrop blur glass |
| **Accents** | `--color-accent` | `#4EE86A` | Neon green identity |
| | `--color-accent-secondary` | `#10B981` | Emerald gradient accent |
| | `--color-accent-muted` | `#1B4D25` | Subdued green borders & indicators |
| **Text** | `--color-text-primary` | `#F2F7F4` | Primary body text |
| | `--color-text-secondary` | `#A8C4B0` | Subtitles & secondary labels |
| | `--color-text-muted` | `#5C7A63` | Telemetry & captions |
| **Borders** | `--color-border` | `rgba(78, 232, 106, 0.12)` | Subtle container border |
| | `--color-border-hover` | `rgba(78, 232, 106, 0.35)` | Active/Hover border glow |

---

## 🔤 Typography System

- **Playfair Display** (`var(--font-playfair)`): Used exclusively for serif page titles and major section headings.
- **Inter** (`var(--font-inter)`): Primary sans-serif font for UI text, buttons, and body content.
- **Space Mono** (`var(--font-mono)`): Technical monospace font for metrics, status telemetry, and scientific labels.

---

## 🎬 Animation Rules

1. **Max Duration**: Interactive UI transitions must not exceed `300ms` (standard: `200ms - 250ms`).
2. **Easing Curves**: Use `cubic-bezier(0.16, 1, 0.3, 1)` (out-expo) for natural, swift UI responses.
3. **Background Motions**: Background shaders, particles, and fog use slow, ambient loops (`5s - 20s`).
4. **Scroll Triggers**: Use the `useAnimation()` hook (IntersectionObserver) to trigger enter animations when elements scroll into view.

---

## 📦 Component Usage Examples

### 1. Button Usage
```tsx
import { PrimaryButton, SecondaryButton } from '@/components/ui';

<PrimaryButton size="md" onClick={handleSave}>
  Save Farm Profile
</PrimaryButton>
```

### 2. Glass Card & Metric
```tsx
import { GlassCard, Metric, Label } from '@/components/ui';

<GlassCard padding="20px" glow>
  <Label>SOIL MOISTURE</Label>
  <Metric value={68} suffix="%" />
</GlassCard>
```

### 3. Living Background
```tsx
import Background from '@/background/Background/Background';

// Full ambient engine
<Background fireflies seeds groundGlow fog shader />
```

### 4. Page Template
```tsx
import { DashboardTemplate } from '@/features';

<DashboardTemplate
  header={<Header />}
  metricsRow={<MetricsGrid />}
  mainContent={<MainChart />}
  sideContent={<WeatherCard />}
/>
```

---

## 🏷️ Naming Conventions

- **Components**: PascalCase (`PrimaryButton.tsx`, `GlassCard.tsx`).
- **Hooks**: camelCase starting with `use` (`useAnimation.ts`, `useCounter.ts`).
- **Tokens/Styles**: kebab-case for CSS variables (`--color-bg-primary`).
- **Templates**: `*Template.tsx` suffix.
