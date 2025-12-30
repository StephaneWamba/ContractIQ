# Frontend Setup Guide

## Quick Start

1. **Initialize Next.js project** (run from ContractIQ directory):
   ```bash
   npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*"
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install @tanstack/react-query @tanstack/react-table lucide-react zod react-hook-form @hookform/resolvers date-fns clsx tailwind-merge
   npm install -D @types/node @types/react @types/react-dom
   ```

3. **Install shadcn/ui**:
   ```bash
   npx shadcn-ui@latest init
   # Choose: Default style, Base color (slate), CSS variables: yes
   ```

4. **Install shadcn/ui components** (one by one as needed):
   ```bash
   npx shadcn-ui@latest add button
   npx shadcn-ui@latest add card
   npx shadcn-ui@latest add table
   npx shadcn-ui@latest add dialog
   npx shadcn-ui@latest add dropdown-menu
   npx shadcn-ui@latest add input
   npx shadcn-ui@latest add badge
   npx shadcn-ui@latest add tabs
   npx shadcn-ui@latest add select
   npx shadcn-ui@latest add textarea
   npx shadcn-ui@latest add toast
   npx shadcn-ui@latest add separator
   npx shadcn-ui@latest add skeleton
   npx shadcn-ui@latest add avatar
   npx shadcn-ui@latest add sheet
   ```

5. **Set up environment variables**:
   Create `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8002/api/v1
   ```

6. **Run development server**:
   ```bash
   npm run dev
   ```

## Project Structure

```
frontend/
├── app/                      # Next.js App Router
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home page
│   ├── (dashboard)/         # Dashboard routes group
│   │   ├── layout.tsx       # Dashboard layout (sidebar, header)
│   │   ├── documents/       # Documents pages
│   │   ├── review/          # Review pages
│   │   └── qa/              # Q&A pages
│   └── api/                 # API routes (if needed)
├── components/              # React components
│   ├── ui/                  # shadcn/ui components
│   ├── layout/              # Layout components
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── Breadcrumbs.tsx
│   ├── documents/           # Document-related components
│   ├── clauses/             # Clause-related components
│   ├── risk/                # Risk-related components
│   └── qa/                  # Q&A components
├── lib/                     # Utilities
│   ├── api/                 # API client
│   ├── utils.ts             # Utility functions
│   └── types.ts             # TypeScript types
├── hooks/                   # Custom React hooks
└── styles/                  # Global styles
```


