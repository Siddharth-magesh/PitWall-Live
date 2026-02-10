# Frontend Tasks

## Overview

Detailed task breakdown for the PitWall Live frontend application built with Next.js 14, React, and TypeScript.

---

## Project Setup

### FE-001: Initialize Next.js 14 Project
**Priority:** P0 | **Effort:** S | **Dependencies:** None

**Description:**
Set up the Next.js 14 project with App Router, TypeScript, and essential configurations.

**Acceptance Criteria:**
- [ ] Next.js 14 initialized with App Router
- [ ] TypeScript configured with strict mode
- [ ] ESLint and Prettier configured
- [ ] Git hooks set up (husky, lint-staged)
- [ ] Basic folder structure created
- [ ] Environment variables configured

**Technical Notes:**
```bash
npx create-next-app@latest pitwall-live --typescript --tailwind --app --src-dir
```

---

### FE-002: Configure TailwindCSS + shadcn/ui
**Priority:** P0 | **Effort:** S | **Dependencies:** FE-001

**Description:**
Set up TailwindCSS with custom theme and install shadcn/ui component library.

**Acceptance Criteria:**
- [ ] TailwindCSS configured with custom colors
- [ ] Dark mode support enabled
- [ ] shadcn/ui initialized
- [ ] Core components installed (Button, Card, Input, etc.)
- [ ] Custom theme variables defined
- [ ] Font configuration (Inter, monospace for data)

**Custom Theme:**
```typescript
// F1-inspired color palette
const colors = {
  f1Red: '#E10600',
  pitlane: '#1E1E1E',
  sector1: '#FFD700',  // Yellow
  sector2: '#00FF00',  // Green
  sector3: '#FF00FF',  // Purple
  compound: {
    soft: '#FF0000',
    medium: '#FFFF00',
    hard: '#FFFFFF',
    intermediate: '#00FF00',
    wet: '#0000FF',
  }
}
```

---

## Layout & Navigation

### FE-003: Implement Layout and Navigation
**Priority:** P0 | **Effort:** M | **Dependencies:** FE-002

**Description:**
Create the main application layout with header, sidebar, and responsive navigation.

**Acceptance Criteria:**
- [ ] Responsive header with logo and user menu
- [ ] Collapsible sidebar navigation
- [ ] Mobile-friendly hamburger menu
- [ ] Breadcrumb navigation
- [ ] Active route highlighting
- [ ] Session/race context selector

**Components to Create:**
- `Header`
- `Sidebar`
- `NavigationMenu`
- `Breadcrumb`
- `SessionSelector`
- `UserMenu`

---

## Data Layer

### FE-004: Create API Client Layer
**Priority:** P0 | **Effort:** M | **Dependencies:** FE-001

**Description:**
Implement a type-safe API client for communicating with the backend.

**Acceptance Criteria:**
- [ ] Axios/fetch wrapper with interceptors
- [ ] TypeScript types for all API responses
- [ ] Error handling and retry logic
- [ ] Request/response logging (dev mode)
- [ ] Authentication header injection

**Implementation:**
```typescript
// api/client.ts
import { createClient } from '@/lib/api';

export const api = createClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 10000,
});

// api/hooks/useTiming.ts
export function useTiming(sessionKey: string) {
  return useQuery({
    queryKey: ['timing', sessionKey],
    queryFn: () => api.get(`/timing/${sessionKey}`),
    refetchInterval: 1000,
  });
}
```

---

### FE-005: Implement WebSocket Integration
**Priority:** P1 | **Effort:** M | **Dependencies:** FE-004

**Description:**
Set up WebSocket connection for real-time data updates.

**Acceptance Criteria:**
- [ ] Socket.io client configured
- [ ] Automatic reconnection handling
- [ ] Connection state management
- [ ] Event subscription system
- [ ] React hooks for WebSocket data

**Implementation:**
```typescript
// hooks/useSocket.ts
export function useSocket<T>(
  channel: string,
  onMessage: (data: T) => void
) {
  const socket = useSocketContext();

  useEffect(() => {
    socket.on(channel, onMessage);
    return () => socket.off(channel, onMessage);
  }, [channel, onMessage]);
}
```

---

## Live Timing Components

### LT-001: Design Timing Table Component
**Priority:** P0 | **Effort:** M | **Dependencies:** FE-002

**Description:**
Create the main live timing table showing driver positions, gaps, and sector times.

**Acceptance Criteria:**
- [ ] Responsive table with sticky header
- [ ] Driver row with position, name, team color
- [ ] Gap and interval columns
- [ ] Sector time columns with color coding
- [ ] Tire compound indicator
- [ ] Pit stop count
- [ ] Row animation on position change

**Component Props:**
```typescript
interface TimingTableProps {
  timing: DriverTiming[];
  showSectors?: boolean;
  highlightDrivers?: string[];
  onDriverClick?: (driverId: string) => void;
}
```

---

### LT-002: Implement Real-time Position Updates
**Priority:** P0 | **Effort:** M | **Dependencies:** LT-001, FE-005

**Description:**
Add real-time updates to the timing table via WebSocket.

**Acceptance Criteria:**
- [ ] Positions update without full re-render
- [ ] Smooth row reordering animation
- [ ] Visual indicator for recent changes
- [ ] Optimistic UI updates
- [ ] Fallback to polling if WS fails

---

### LT-003: Add Sector Time Visualization
**Priority:** P0 | **Effort:** M | **Dependencies:** LT-001

**Description:**
Implement sector time display with proper color coding.

**Acceptance Criteria:**
- [ ] Three sector time columns
- [ ] Color coding: purple (best), green (personal best), yellow (normal)
- [ ] Mini-sector breakdown on hover
- [ ] Comparison mode with baseline driver

---

## Telemetry Components

### TEL-001: Implement Speed Trace Chart
**Priority:** P1 | **Effort:** M | **Dependencies:** FE-002

**Description:**
Create an interactive speed trace chart for lap analysis.

**Acceptance Criteria:**
- [ ] Line chart with smooth rendering
- [ ] Multiple driver overlay support
- [ ] Zoom and pan functionality
- [ ] Synchronized cursor across charts
- [ ] Distance or time x-axis toggle
- [ ] Export as image

**Library Choice:** Recharts or D3.js

---

### TEL-004: Implement Lap Comparison Tool
**Priority:** P1 | **Effort:** L | **Dependencies:** TEL-001

**Description:**
Build a comprehensive lap comparison tool.

**Acceptance Criteria:**
- [ ] Select multiple drivers and laps
- [ ] Side-by-side telemetry view
- [ ] Delta time chart
- [ ] Corner-by-corner breakdown
- [ ] Mini-sector analysis
- [ ] Save comparison for sharing

---

## ML Playground UI

### MLP-001: Design ML Playground UI
**Priority:** P1 | **Effort:** M | **Dependencies:** FE-002

**Description:**
Design the main ML playground interface.

**Acceptance Criteria:**
- [ ] Model template gallery
- [ ] Training configuration wizard
- [ ] Progress monitoring dashboard
- [ ] Results visualization
- [ ] Model management panel

**Wireframe:**
```
┌─────────────────────────────────────────────────────────────┐
│  ML Playground                                    [New Model]│
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ Race Winner │ │  Lap Time   │ │   Custom    │           │
│  │  Predictor  │ │  Predictor  │ │   Model     │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                              │
│  Your Models                                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ race_winner_v2  │ Training │ ████████░░ 80% │ 12m left │ │
│  │ quali_order_v1  │ Ready    │ Acc: 62%      │ Deploy   │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Commentary UI

### COM-UI-001: Commentary Display Component
**Priority:** P1 | **Effort:** M | **Dependencies:** FE-002

**Description:**
Create the live commentary display component.

**Acceptance Criteria:**
- [ ] Streaming text display with typing effect
- [ ] Commentary history with timestamps
- [ ] Style indicator (technical/casual/dramatic)
- [ ] Mute/unmute controls
- [ ] Font size adjustment
- [ ] Auto-scroll with manual override

---

## State Management

### STATE-001: Set Up Zustand Store
**Priority:** P0 | **Effort:** M | **Dependencies:** FE-001

**Description:**
Implement global state management with Zustand.

**Stores to Create:**
```typescript
// stores/session.ts
interface SessionStore {
  currentSession: Session | null;
  setSession: (session: Session) => void;
}

// stores/preferences.ts
interface PreferencesStore {
  commentaryStyle: 'technical' | 'casual' | 'dramatic';
  favoriteDrivers: string[];
  theme: 'light' | 'dark' | 'system';
  setCommentaryStyle: (style: string) => void;
  toggleFavoriteDriver: (driverId: string) => void;
}

// stores/realtime.ts
interface RealtimeStore {
  timing: DriverTiming[];
  positions: Position[];
  updateTiming: (update: TimingUpdate) => void;
}
```

---

## Testing

### FE-TEST-001: Component Unit Tests
**Priority:** P0 | **Effort:** L | **Dependencies:** FE-*

**Description:**
Write unit tests for all components using Vitest and React Testing Library.

**Coverage Targets:**
- Components: 80%
- Hooks: 90%
- Utilities: 100%

---

### FE-TEST-002: E2E Tests
**Priority:** P1 | **Effort:** L | **Dependencies:** All frontend

**Description:**
Implement end-to-end tests with Playwright.

**Key Flows to Test:**
- [ ] User authentication
- [ ] Live timing page load and updates
- [ ] Telemetry comparison workflow
- [ ] ML model training wizard
- [ ] Commentary toggle and settings

---

## Performance

### FE-PERF-001: Code Splitting
**Priority:** P1 | **Effort:** M | **Dependencies:** FE-001

**Description:**
Implement code splitting for optimal loading.

**Tasks:**
- [ ] Route-based splitting (automatic with App Router)
- [ ] Dynamic imports for heavy components
- [ ] Lazy load telemetry charts
- [ ] Prefetch on hover for navigation

---

## Accessibility

### FE-A11Y-001: WCAG 2.1 Compliance
**Priority:** P1 | **Effort:** M | **Dependencies:** All UI

**Description:**
Ensure the application meets WCAG 2.1 AA standards.

**Tasks:**
- [ ] Keyboard navigation
- [ ] Screen reader support
- [ ] Color contrast compliance
- [ ] Focus management
- [ ] ARIA labels
- [ ] Skip links
