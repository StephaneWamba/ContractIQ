# ContractIQ - UI/UX Design Document

## Design Principles

### 1. **Professional & Trustworthy**
- Clean, modern interface that inspires confidence
- Professional color scheme (blues, grays, whites)
- Clear typography hierarchy
- Consistent spacing and alignment

### 2. **Efficient & Intuitive**
- Information hierarchy that guides the user naturally
- Common workflows accessible in 2-3 clicks
- Clear visual feedback for all actions
- Keyboard shortcuts for power users

### 3. **Data-Dense but Readable**
- Tables and lists optimized for scanning
- Risk indicators that are immediately obvious
- Color coding for status and severity
- Expandable/collapsible sections to manage complexity

### 4. **Responsive & Accessible**
- Mobile-friendly (responsive design)
- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader friendly

---

## Color Palette

### Primary Colors
- **Primary Blue**: `#2563eb` (Blue 600) - Main actions, links, active states
- **Primary Blue Dark**: `#1e40af` (Blue 700) - Hover states
- **Primary Blue Light**: `#3b82f6` (Blue 500) - Subtle accents

### Semantic Colors
- **Critical Risk**: `#dc2626` (Red 600) - Critical risks
- **High Risk**: `#ea580c` (Orange 600) - High risks
- **Medium Risk**: `#ca8a04` (Yellow 600) - Medium risks
- **Low Risk**: `#16a34a` (Green 600) - Low risks
- **Success**: `#10b981` (Green 500) - Success states
- **Warning**: `#f59e0b` (Amber 500) - Warnings
- **Error**: `#ef4444` (Red 500) - Errors
- **Info**: `#3b82f6` (Blue 500) - Information

### Neutral Colors
- **Background**: `#ffffff` - Main background
- **Surface**: `#f9fafb` (Gray 50) - Cards, panels
- **Border**: `#e5e7eb` (Gray 200) - Borders, dividers
- **Text Primary**: `#111827` (Gray 900) - Main text
- **Text Secondary**: `#6b7280` (Gray 500) - Secondary text
- **Text Muted**: `#9ca3af` (Gray 400) - Muted text

### Dark Mode (Future)
- Background: `#111827` (Gray 900)
- Surface: `#1f2937` (Gray 800)
- Text Primary: `#f9fafb` (Gray 50)

---

## Typography

### Font Family
- **Primary**: Inter (modern, readable, professional)
- **Fallback**: system-ui, -apple-system, sans-serif

### Font Sizes
- **H1**: 2.25rem (36px) - Page titles
- **H2**: 1.875rem (30px) - Section headers
- **H3**: 1.5rem (24px) - Subsection headers
- **H4**: 1.25rem (20px) - Card titles
- **Body Large**: 1.125rem (18px) - Important body text
- **Body**: 1rem (16px) - Standard body text
- **Body Small**: 0.875rem (14px) - Secondary text, captions
- **Body XSmall**: 0.75rem (12px) - Labels, metadata

### Font Weights
- **Light**: 300 - Rarely used
- **Regular**: 400 - Body text
- **Medium**: 500 - Emphasis, labels
- **Semibold**: 600 - Headings, buttons
- **Bold**: 700 - Strong emphasis

---

## Layout Structure

### Main Layout (App Shell)

```
┌─────────────────────────────────────────────────────────┐
│  Header (fixed)                                         │
│  ┌──────────┐  Logo  │  Workspace Selector  │  User    │
├──┼──────────┼──────────────────────────────────────────┤
│  │          │                                         │
│  │ Sidebar  │  Main Content Area                      │
│  │ (collap.)│                                         │
│  │          │  ┌───────────────────────────────────┐ │
│  │ • Home   │  │  Breadcrumbs                      │ │
│  │ • Docs   │  │  ───────────────────────────────  │ │
│  │ • Q&A    │  │                                   │ │
│  │ • Review │  │  Content                          │ │
│  │          │  │                                   │ │
│  │          │  │                                   │ │
└──┴──────────┴──┴───────────────────────────────────┘ │
```

### Key Layout Features
- **Fixed Header**: Always visible workspace selector and user menu
- **Collapsible Sidebar**: Navigation that can collapse to icons only
- **Flexible Content Area**: Adapts to different page types
- **Breadcrumbs**: Clear navigation hierarchy
- **Sticky Filters**: Filter panels stick when scrolling

---

## Page Designs

### 1. Dashboard / Workspace Home

**Layout:**
- Welcome section with workspace name
- Quick stats cards (Total Documents, Documents Reviewed, Risks Found)
- Recent documents list
- Quick actions (Upload Document, Ask Question)

**Components:**
```
┌────────────────────────────────────────────────────┐
│  Welcome back, [Workspace Name]                   │
│                                                    │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐          │
│  │ Docs │  │Reviewed│ │ Risks│  │Q&As  │          │
│  │  12  │  │   8   │  │  23  │  │  5   │          │
│  └──────┘  └──────┘  └──────┘  └──────┘          │
│                                                    │
│  Recent Documents                    [+ Upload]    │
│  ┌────────────────────────────────────────────┐   │
│  │ 📄 Vendor Agreement.pdf                    │   │
│  │    3 pages • Processed • 15 clauses       │   │
│  │    🔴 2 Critical • 🟠 3 High              │   │
│  └────────────────────────────────────────────┘   │
```

---

### 2. Documents List Page

**Layout:**
- Search bar at top
- Filter chips (Status, Risk Level, Date)
- Document cards/table view toggle
- Pagination or infinite scroll

**Card View:**
```
┌────────────────────────────────────────────────────┐
│  Documents                    [Search...] [+ Upload]│
│  ┌────────────────────────────────────────────┐   │
│  │ 📄 Vendor Agreement.pdf                    │   │
│  │    Processed • 3 pages • 15 clauses       │   │
│  │    🔴 Critical: 2  🟠 High: 3  🟡 Med: 5  │   │
│  │    Updated 2 hours ago                     │   │
│  │    [View] [Delete]                         │   │
│  └────────────────────────────────────────────┘   │
```

**Table View:**
```
┌─────────────────────────────────────────────────────────┐
│ Name              │ Status    │ Pages │ Clauses │ Risks │
├───────────────────┼───────────┼───────┼─────────┼───────┤
│ Vendor Agreement  │ Processed │   3   │   15    │ 🔴2🟠3│
│ Service Contract  │ Processing│   5   │   -     │   -   │
```

---

### 3. Contract Review Page (Main Focus)

**Layout:**
- Split view: Left panel (clause list), Right panel (detail view)
- Or single view with tabs: Overview, Clauses, Risks, Review
- Sticky risk summary panel

**Split View Design:**
```
┌──────────────────────────────────────────────────────────┐
│  Vendor Agreement.pdf          [Export] [Share] [Settings]│
├──────────────┬───────────────────────────────────────────┤
│              │  Overview Tab                              │
│  Risk Summary│  ─────────────────────────────────────    │
│  ─────────── │  Document Info                            │
│  🔴 Critical │  • 3 pages                                │
│  ─────────── │  • 15 clauses extracted                   │
│  2           │  • Processed 2 hours ago                  │
│              │                                            │
│  🟠 High     │  Risk Breakdown                           │
│  ─────────── │  🔴 Critical: 2                           │
│  3           │  🟠 High: 3                               │
│              │  🟡 Medium: 5                             │
│  🟡 Medium   │  🟢 Low: 5                                │
│  ─────────── │                                            │
│  5           │  [Switch to Clauses Tab]                  │
│              │                                            │
│  🟢 Low      │                                            │
│  ─────────── │                                            │
│  5           │                                            │
│              │                                            │
│  [All Clauses]│                                           │
│  [Filter...] │                                           │
└──────────────┴───────────────────────────────────────────┘

Clauses Tab:
┌──────────────┬───────────────────────────────────────────┤
│              │  Clauses                          [Filter]│
│  Risk Summary│  ─────────────────────────────────────    │
│  (sticky)    │                                            │
│              │  Type │ Text Preview │ Page │ Risk │Action│
│              │ ──────┼──────────────┼──────┼──────┼──────│
│              │ Term. │ "Either     │  3   │ 🔴   │ [View]│
│              │       │  party..."  │      │      │      │
│              │ Indem.│ "Vendor     │  2   │ 🔴   │ [View]│
│              │       │  will..."   │      │      │      │
│              │ Liab. │ "Vendor     │  2   │ 🟠   │ [View]│
│              │       │  agrees..." │      │      │      │
└──────────────┴───────────────────────────────────────────┘
```

**Clause Detail View (Modal or Side Panel):**
```
┌──────────────────────────────────────────────────────────┐
│  Termination Clause                    [Close] [Previous]│
├──────────────────────────────────────────────────────────┤
│  Type: Termination                                       │
│  Page: 3 • Section: Term of Agreement                    │
│  Confidence: 85%                                         │
│                                                           │
│  Risk Level: 🔴 Critical                                 │
│                                                           │
│  Extracted Text:                                         │
│  ┌───────────────────────────────────────────────────┐   │
│  │ This agreement will commence on the date of       │   │
│  │ execution and remain in force until terminated    │   │
│  │ by either party with or without cause.            │   │
│  │ Termination must be in writing.                   │   │
│  └───────────────────────────────────────────────────┘   │
│                                                           │
│  Risk Flags:                                             │
│  • ⚠️ Unilateral termination without cause               │
│  • ⚠️ No notice period required                          │
│                                                           │
│  [View in Document]  [Add Note]  [Mark Reviewed]        │
└──────────────────────────────────────────────────────────┘
```

---

### 4. Q&A Chat Interface

**Layout:**
- Left sidebar: Conversation list
- Main area: Chat messages with citations
- Input area: Question input with suggestions

**Design:**
```
┌──────────────────────────────────────────────────────────┐
│  Q&A Assistant                        [New Conversation] │
├──────────┬───────────────────────────────────────────────┤
│          │  What are the termination clauses?            │
│Conv. 1   │  ────────────────────────────────────────    │
│          │                                               │
│Conv. 2   │  🤖 Assistant                                │
│          │  The termination clauses are:                │
│          │                                               │
│Conv. 3   │  • Either party can terminate with or        │
│          │    without cause                             │
│          │  • Termination must be in writing            │
│          │                                               │
│          │  Sources:                                    │
│          │  [1] Vendor Agreement.pdf, Page 3            │
│          │  [2] Vendor Agreement.pdf, Page 3            │
│          │                                               │
│          │  👤 You                                     │
│          │  What is the liability limit?                │
│          │                                               │
│          │  [Type your question...]  [📎] [Send]       │
│          │                                               │
│          │  💡 Suggested questions:                    │
│          │  • What are the payment terms?               │
│          │  • What IP rights are mentioned?             │
└──────────┴───────────────────────────────────────────────┘
```

---

### 5. Document Upload Page

**Design:**
```
┌──────────────────────────────────────────────────────────┐
│  Upload Document                                         │
│  ────────────────────────────────────────────────────    │
│                                                           │
│  ┌─────────────────────────────────────────────────┐     │
│  │                                                   │     │
│  │              📄 Drop files here                  │     │
│  │        or click to browse                        │     │
│  │                                                   │     │
│  │        Supported: PDF, DOCX (Max 50MB)           │     │
│  │                                                   │     │
│  └─────────────────────────────────────────────────┘     │
│                                                           │
│  Upload Queue:                                           │
│  ┌─────────────────────────────────────────────────┐     │
│  │ 📄 contract.pdf                          [Remove]│     │
│  │   2.3 MB • Ready to upload                      │     │
│  └─────────────────────────────────────────────────┘     │
│                                                           │
│  [Cancel]                    [Upload Documents]          │
└──────────────────────────────────────────────────────────┘
```

---

## Component Specifications

### 1. Risk Badge Component
```tsx
// Critical Risk
<RiskBadge level="critical">🔴 Critical</RiskBadge>

// Visual: Red background with white text, rounded pill
// Colors: bg-red-600 text-white
// Size: Small (0.75rem padding), Medium (default), Large
```

### 2. Status Badge Component
```tsx
// Processing
<StatusBadge status="processing">Processing</StatusBadge>

// Visual: Spinning icon + text
// Processing: Blue with spinner
// Processed: Green checkmark
// Failed: Red X
```

### 3. Clause Card Component
```tsx
<ClauseCard
  type="Termination"
  text="Either party can terminate..."
  page={3}
  riskLevel="critical"
  confidence={0.85}
  onClick={() => openDetail(clause)}
/>
```

### 4. Citation Component
```tsx
<Citation
  index={1}
  document="Vendor Agreement.pdf"
  page={3}
  section="Term of Agreement"
  excerpt="Either party can terminate..."
  onClick={() => scrollToPage(3)}
/>
```

### 5. Risk Summary Panel
```tsx
<RiskSummaryPanel
  critical={2}
  high={3}
  medium={5}
  low={5}
  onFilter={(level) => filterByRisk(level)}
/>
```

---

## Interaction Patterns

### 1. Hover States
- Cards: Subtle elevation (shadow increase)
- Buttons: Background color darken
- Links: Underline on hover
- Table rows: Background color change

### 2. Loading States
- Skeleton screens for content loading
- Progress bars for uploads
- Spinners for quick actions
- Optimistic UI updates where possible

### 3. Empty States
- Friendly illustrations or icons
- Clear call-to-action
- Helpful messaging
- Example: "No documents yet. Upload your first contract to get started!"

### 4. Error States
- Clear error messages
- Suggested actions
- Retry buttons where applicable
- Non-blocking notifications

### 5. Success States
- Toast notifications for actions
- Confirmation modals for destructive actions
- Success badges/icons
- Smooth transitions

---

## Responsive Breakpoints

- **Mobile**: < 640px (sm)
- **Tablet**: 640px - 1024px (md, lg)
- **Desktop**: > 1024px (xl, 2xl)

### Mobile Adaptations
- Sidebar collapses to bottom navigation or hamburger menu
- Tables convert to cards
- Split views become stacked
- Touch-friendly button sizes (min 44x44px)

---

## Accessibility Features

1. **Keyboard Navigation**
   - Tab order follows visual flow
   - Escape closes modals
   - Enter/Space activates buttons
   - Arrow keys navigate lists/tables

2. **Screen Readers**
   - Semantic HTML
   - ARIA labels where needed
   - Live regions for dynamic content
   - Skip links

3. **Visual**
   - Color contrast ratios meet WCAG AA
   - Focus indicators visible
   - Text alternatives for icons
   - Scalable text (up to 200%)

---

## Animation & Transitions

### Principles
- Subtle and purposeful
- Fast (< 300ms for most)
- Easing: ease-in-out for most, ease-out for entrances

### Specific Animations
- **Page transitions**: Fade in (200ms)
- **Modal**: Slide up + fade (300ms)
- **Tooltips**: Fade in (150ms)
- **Dropdowns**: Slide down (200ms)
- **Cards hover**: Shadow increase (150ms)

---

## Icons

**Icon Library**: Lucide React (consistent, modern, accessible)

**Common Icons:**
- 📄 File/Document
- 🔍 Search
- ⚠️ Warning/Risk
- ✅ Check/Success
- ❌ Error/Delete
- 📊 Analytics/Stats
- 💬 Chat/Message
- 📤 Upload
- 🔒 Lock/Secure
- ⚙️ Settings
- 👤 User
- 🏢 Workspace

---

## Design Tokens

```ts
const tokens = {
  spacing: {
    xs: '0.25rem',  // 4px
    sm: '0.5rem',   // 8px
    md: '1rem',     // 16px
    lg: '1.5rem',   // 24px
    xl: '2rem',     // 32px
    '2xl': '3rem',  // 48px
  },
  borderRadius: {
    sm: '0.25rem',  // 4px
    md: '0.5rem',   // 8px
    lg: '0.75rem',  // 12px
    xl: '1rem',     // 16px
    full: '9999px', // Pill
  },
  shadows: {
    sm: '0 1px 2px rgba(0,0,0,0.05)',
    md: '0 4px 6px rgba(0,0,0,0.1)',
    lg: '0 10px 15px rgba(0,0,0,0.1)',
    xl: '0 20px 25px rgba(0,0,0,0.1)',
  },
  transitions: {
    fast: '150ms',
    normal: '200ms',
    slow: '300ms',
  },
}
```

---

## Implementation Notes

1. **Component Library**: Use shadcn/ui as base, customize as needed
2. **Styling**: Tailwind CSS with custom design tokens
3. **State Management**: TanStack Query for server state, Zustand/Context for UI state
4. **Forms**: React Hook Form + Zod validation
5. **Tables**: TanStack Table for advanced table features
6. **Charts**: Recharts for risk summaries (if needed)

---

This design provides a professional, modern, and efficient UI for contract review while maintaining excellent UX principles.


