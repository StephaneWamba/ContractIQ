# ContractIQ Frontend

Modern, professional frontend for ContractIQ built with Next.js 14, TypeScript, Tailwind CSS, and shadcn/ui.

## Features

- 🎨 **Modern UI/UX**: Clean, professional design with excellent user experience
- ⚡ **Fast**: Next.js App Router for optimal performance
- 📱 **Responsive**: Works seamlessly on desktop, tablet, and mobile
- ♿ **Accessible**: WCAG 2.1 AA compliant
- 🎯 **Type-Safe**: Full TypeScript support
- 🧩 **Component-Based**: Reusable components with shadcn/ui
- 🔄 **State Management**: TanStack Query for server state

## Getting Started

See `FRONTEND_SETUP.md` for detailed setup instructions.

Quick start:

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see the app.

## Project Structure

- `app/` - Next.js App Router pages and layouts
- `components/` - React components
  - `ui/` - shadcn/ui components
  - `layout/` - Layout components (Header, Sidebar, etc.)
  - `documents/` - Document-related components
  - `clauses/` - Clause-related components
  - `risk/` - Risk-related components
  - `qa/` - Q&A components
- `lib/` - Utilities and API client
- `hooks/` - Custom React hooks
- `styles/` - Global styles

## Design System

See `../UI_UX_DESIGN.md` for the complete design system documentation.

## API Integration

The frontend communicates with the backend API at `NEXT_PUBLIC_API_URL` (default: `http://localhost:8002/api/v1`).

API client is located in `lib/api/`.

## Building for Production

```bash
npm run build
npm start
```

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui
- **State**: TanStack Query
- **Forms**: React Hook Form + Zod
- **Tables**: TanStack Table
- **Icons**: Lucide React
- **Date**: date-fns


